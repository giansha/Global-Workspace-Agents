"""
CognitiveEngine — implements Algorithm 1 from the paper (§3.1–3.5).

Orchestrates the four-phase Cognitive Tick loop:
  Phase 1: Perceive & Retrieve
  Phase 2: Think (entropy-regulated generation + critique)
  Phase 3: Arbitrate (Meta selects W_t and transition tag)
  Phase 4: Update (STM bifurcation + state transition)

Yields TickSnapshot dicts after each tick so the UI can render progress live.
"""
from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field
from typing import Generator, List, Optional, Tuple

logger = logging.getLogger("gwa.timing")

from config import GWAConfig
from workspace import GlobalWorkspace
from agents.attention import AttentionNode
from agents.generator import GeneratorNode
from agents.critic import CriticNode
from agents.meta import MetaNode
from agents.response import ResponseNode


@dataclass
class TickSnapshot:
    """Carries all observable data from a single cognitive tick for the UI."""
    tick: int
    rag_queries: List[str]
    rag_context: str
    entropy: float
    T_gen: float
    candidates: List[str]
    evaluations: List[Tuple[int, str]]   # (score, critique) per candidate
    winning_thought: str
    transition_tag: str                  # "THINK_MORE" or "RESPONSE"
    stm_token_count: int
    compressed: bool = False
    final_response: Optional[str] = None  # set when tag == RESPONSE


class CognitiveEngine:
    """
    Event-driven execution engine for the GWA cognitive cycle.

    One engine instance persists for the lifetime of the workspace so that
    STM, LTM, and entropy state accumulate across user turns.
    """

    def __init__(self, config: GWAConfig) -> None:
        self.config = config
        self.workspace = GlobalWorkspace(config)

        # Instantiate heterogeneous agent swarm
        _args = dict(
            api_base_url=config.api_base_url,
            api_key=config.api_key,
            model=config.chat_model,
        )
        self.attention = AttentionNode(**_args)
        self.generator = GeneratorNode(**_args)
        self.critic = CriticNode(**_args)
        self.meta = MetaNode(**_args)
        self.response = ResponseNode(**_args)

    # ── Public Entry Point ────────────────────────────────────────────────────

    def run(self, user_input: str, debug_callback=None) -> Generator[TickSnapshot, None, None]:
        """
        Process one user turn through up to max_ticks cognitive cycles.

        Yields a TickSnapshot after each tick. The last snapshot in a turn
        has `transition_tag == "RESPONSE"` and carries `final_response`.

        Parameters
        ----------
        debug_callback:  Optional callable(agent: str, tick: int, token: str).
                         When provided, each agent streams tokens through this
                         callback so the UI can display real-time agent output.
        """
        ws = self.workspace
        cfg = self.config

        ws.current_input = user_input

        for _ in range(cfg.max_ticks):
            tick = ws.tick
            compressed = False
            _tick_start = time.perf_counter()

            # Helper: build a per-agent, per-tick token callback
            def make_cb(agent_name: str, tick_num: int):
                if debug_callback is None:
                    return None
                def cb(token: str):
                    debug_callback(agent_name, tick_num, token)
                return cb

            # ── Phase 1: Perceive & Retrieve ─────────────────────────────────
            _t = time.perf_counter()
            rag_queries = self.attention.run(
                stm_context=ws.stm.get_context_string(),
                current_input=ws.current_input,
                debug_callback=make_cb("attention", tick),
                max_tokens=cfg.attention_max_tokens,
            )
            logger.info("[tick %d] attention:    %.3fs", tick, time.perf_counter() - _t)

            _t = time.perf_counter()
            rag_context = ws.ltm.retrieve_multi(rag_queries, top_k=cfg.top_k_rag)
            ws.rag_context = rag_context
            logger.info("[tick %d] rag_retrieve: %.3fs  (queries=%d)", tick, time.perf_counter() - _t, len(rag_queries))

            # Build illuminated global state S_t
            state_str = ws.build_state_string()

            # ── Phase 2: Think ────────────────────────────────────────────────
            T_gen = ws.entropy_drive.compute_T_gen()
            entropy = ws.entropy_drive.last_entropy

            _t = time.perf_counter()
            candidates = self.generator.run(
                state_string=state_str,
                T_gen=T_gen,
                N=cfg.N,
                debug_callback=make_cb("generator", tick),
                max_tokens=cfg.generator_max_tokens,
            )
            logger.info("[tick %d] generator:   %.3fs", tick, time.perf_counter() - _t)

            _t = time.perf_counter()
            evaluations = self.critic.run(
                state_string=state_str,
                candidates=candidates,
                temperature=cfg.critic_temperature,
                debug_callback=make_cb("critic", tick),
                max_tokens=cfg.critic_max_tokens,
            )
            logger.info("[tick %d] critic:      %.3fs", tick, time.perf_counter() - _t)

            # ── Phase 3: Arbitrate ────────────────────────────────────────────
            _t = time.perf_counter()
            winning_thought, tag = self.meta.run(
                state_string=state_str,
                candidates=candidates,
                evaluations=evaluations,
                debug_callback=make_cb("meta", tick),
                max_tokens=cfg.meta_max_tokens,
            )
            logger.info("[tick %d] meta:        %.3fs", tick, time.perf_counter() - _t)

            # ── Phase 4: Update ───────────────────────────────────────────────
            # Pre-embed W_t now (single API call); reused by both entropy drive
            # and any LTM store below — avoids a redundant embedding round-trip.
            _t = time.perf_counter()
            winning_embedding: list | None = None
            try:
                result = ws.ltm.embed([winning_thought])
                winning_embedding = result[0] if result else None
            except Exception:
                pass
            logger.info("[tick %d] embed_Wt:    %.3fs", tick, time.perf_counter() - _t)

            # 4a. Memory bifurcation if STM exceeds threshold θ
            if ws.stm.token_count() > cfg.theta:
                summary = self.meta.summarize(ws.stm.get_context_string())
                ws.ltm.store(ws.stm.get_context_string(), metadata={"type": "stm_archive", "tick": tick})# TODO:这里需要提取知识而不是直接存储原文
                ws.stm.compress(summary)
                compressed = True

            # 4b. State transition (eqs. 4–7 in paper)
            if tag == "RESPONSE":
                # Translate internal W_t into natural user-facing speech
                _t = time.perf_counter()
                final_response = self.response.run(
                    winning_thought=winning_thought,
                    stm_context=ws.stm.get_context_string(),
                    user_message=ws.current_input,
                    debug_callback=make_cb("response", tick),
                    max_tokens=cfg.response_max_tokens,
                )
                logger.info("[tick %d] response:    %.3fs", tick, time.perf_counter() - _t)

                ws.stm.append(role="assistant", content=final_response, tick=tick)
                ws.stm.append(role="user", content=ws.current_input + " [RESOLVED]", tick=tick)

                self._update_entropy(winning_thought, embedding=winning_embedding)

                snapshot = TickSnapshot(
                    tick=tick,
                    rag_queries=rag_queries,
                    rag_context=rag_context,
                    entropy=entropy,
                    T_gen=T_gen,
                    candidates=candidates,
                    evaluations=evaluations,
                    winning_thought=winning_thought,
                    transition_tag=tag,
                    stm_token_count=ws.stm.token_count(),
                    compressed=compressed,
                    final_response=final_response,
                )
                logger.info("[tick %d] TOTAL:       %.3fs  → RESPONSE", tick, time.perf_counter() - _tick_start)
                ws.reset_input()
                ws.tick += 1
                yield snapshot
                return

            else:  # THINK_MORE
                ws.stm.append(role="assistant", content=winning_thought, tick=tick)
                ws.current_input = (
                    ws.current_input
                    + "\n[PENDING: External environment awaits response]"
                )

                self._update_entropy(winning_thought, embedding=winning_embedding)

                snapshot = TickSnapshot(
                    tick=tick,
                    rag_queries=rag_queries,
                    rag_context=rag_context,
                    entropy=entropy,
                    T_gen=T_gen,
                    candidates=candidates,
                    evaluations=evaluations,
                    winning_thought=winning_thought,
                    transition_tag=tag,
                    stm_token_count=ws.stm.token_count(),
                    compressed=compressed,
                )
                logger.info("[tick %d] TOTAL:       %.3fs  → THINK_MORE", tick, time.perf_counter() - _tick_start)
                ws.tick += 1
                yield snapshot

        # Safety: max_ticks exceeded — force a response with the last W_t
        fallback = winning_thought if 'winning_thought' in dir() else "I need more time to process this."
        ws.stm.append(role="assistant", content=fallback, tick=ws.tick)
        ws.reset_input()
        yield TickSnapshot(
            tick=ws.tick,
            rag_queries=[],
            rag_context="",
            entropy=ws.entropy_drive.last_entropy,
            T_gen=ws.entropy_drive.last_T_gen,
            candidates=[],
            evaluations=[],
            winning_thought=fallback,
            transition_tag="RESPONSE",
            stm_token_count=ws.stm.token_count(),
            final_response=fallback,
        )

    # ── Internal ──────────────────────────────────────────────────────────────

    def _update_entropy(self, thought: str, embedding: list | None = None) -> None:
        """Update the entropy drive's cluster state.

        If `embedding` is supplied (pre-computed), skips the API call entirely.
        Otherwise falls back to embedding `thought` on demand.
        """
        try:
            if embedding is None:
                result = self.workspace.ltm.embed([thought])
                embedding = result[0] if result else None
            if embedding is not None:
                self.workspace.entropy_drive.update(embedding)
        except Exception:
            pass  # entropy update is best-effort; don't crash the tick

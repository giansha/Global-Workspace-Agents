"""
GlobalWorkspace — the central state tensor S_t (§3.1, §3.2).

S_t = STM_t ∪ INPUT_t ∪ RAG_t ∪ P_Self

P_Self is injected by BaseAgent into every system prompt; here we assemble
the dynamic components (STM, INPUT, RAG) into a formatted string for agents.
"""
from __future__ import annotations

from config import GWAConfig
from memory.stm import ShortTermMemory
from memory.ltm import LongTermMemory
from entropy_drive import EntropyDrive
from typing import List

class GlobalWorkspace:
    """
    Central broadcast hub that maintains the full global state.

    Agents read from `build_state_string()` to get S_t; the engine
    writes back to `stm`, `current_input`, and `rag_context`.
    """

    def __init__(self, config: GWAConfig) -> None:
        self.config = config
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory(
            api_base_url=config.api_base_url,
            api_key=config.api_key,
            embedding_model=config.embedding_model,
            persist_dir=config.chroma_persist_dir,
        )
        self.entropy_drive = EntropyDrive(
            K=config.K,
            tau=config.tau,
            T_base=config.T_base,
            alpha=config.alpha,
            beta=config.beta,
            entropy_window=config.entropy_window,
        )

        self.current_input: str = ""
        self.rag_context: str = ""
        self.last_rag_queries: List[str] = []
        self.last_knowledge: str = ""
        self.tick: int = 0

    # ── State Assembly ────────────────────────────────────────────────────────

    def build_state_string(self) -> str:
        """
        Assemble the full global state S_t = STM ∪ INPUT ∪ RAG as a
        human-readable string for agent prompts. P_Self is injected separately
        by BaseAgent into the system prompt.
        """
        parts: List[str] = []

        stm_str = self.stm.get_context_string()
        if stm_str:
            parts.append(f"=== SHORT-TERM MEMORY (STM) ===\n{stm_str}")

        if self.current_input:
            parts.append(f"=== CURRENT INPUT (INPUT_t) ===\n{self.current_input}")

        if self.rag_context:
            parts.append(f"=== RETRIEVED CONTEXT (RAG_t) ===\n{self.rag_context}")

        return "\n\n".join(parts)

    # ── Convenience ───────────────────────────────────────────────────────────

    def reset_input(self) -> None:
        """Flush INPUT_t after a [RESPONSE] transition."""
        self.current_input = ""
        self.rag_context = ""

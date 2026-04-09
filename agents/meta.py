"""
Meta Node — "Metacognitive Executive" in GWT (§3.6).

Performs contextual metacognition to select the optimal winning thought W_t
and dictates the state transition tag T_t ∈ {[THINK_MORE], [RESPONSE]}.

Also used for STM compression (summarization) during memory bifurcation (§3.5).
"""
from __future__ import annotations

import re
from typing import List, Tuple

from .base import BaseAgent

_SYSTEM_DIRECTIVE = (
    "Given these perspectives and their assessments, which feels most true, "
    "complete, and worth expressing? Select it and decide: is this ready to "
    "share with the person outside, or does it need more thought?\n\n"
    "Output format:\n"
    "WINNING THOUGHT: [full text of the selected perspective]\n"
    "TRANSITION: [RESPONSE] or [THINK_MORE]\n"
    "RATIONALE: [1-2 sentences]"
)

_SUMMARIZE_DIRECTIVE = (
    "I act as the Memory Compression Node. My task is to synthesize a dense, "
    "coherent semantic summary of the provided cognitive history. The summary must "
    "preserve all critical decisions, unresolved threads, and key conclusions. "
    "It should be substantially shorter than the original while maintaining "
    "full narrative continuity. Output only the summary text."
)


class MetaNode(BaseAgent):
    """Arbitrates candidates and controls state transition; also handles STM compression."""

    def run(
        self,
        state_string: str,
        candidates: List[str],
        evaluations: List[Tuple[int, str]],
        debug_callback=None,
        max_tokens: int = 1024,
    ) -> Tuple[str, str]:
        """
        Returns
        -------
        (winning_thought, transition_tag) where tag ∈ {"THINK_MORE", "RESPONSE"}
        """
        numbered_candidates = "\n".join(f"{i+1}. {c}" for i, c in enumerate(candidates))
        numbered_evals = "\n".join(
            f"{i+1}. Score: {score} | Critique: {critique}"
            for i, (score, critique) in enumerate(evaluations)
        )
        user_content = (
            f"Global State (S_t):\n{state_string}\n\n"
            f"Candidate Thoughts:\n{numbered_candidates}\n\n"
            f"Critical Evaluations:\n{numbered_evals}\n\n"
            "I will now execute the final arbitration."
        )
        raw = self.call(
            system_directive=_SYSTEM_DIRECTIVE,
            user_content=user_content,
            temperature=0.3,
            max_tokens=max_tokens,
            token_callback=debug_callback,
        )
        return _parse_meta_output(raw, candidates)

    def summarize(self, stm_context: str) -> str:
        """Generate a dense semantic summary for STM compression (§3.5)."""
        raw = self.call(
            system_directive=_SUMMARIZE_DIRECTIVE,
            user_content=f"Cognitive History to Compress:\n{stm_context}",
            temperature=0.3,
            max_tokens=800,
        )
        return raw.strip()


def _parse_meta_output(raw: str, candidates: List[str]) -> Tuple[str, str]:
    """Extract winning thought and transition tag from Meta output."""
    # Extract tag
    tag = "THINK_MORE"
    if re.search(r"\[RESPONSE\]", raw, re.IGNORECASE):
        tag = "RESPONSE"
    elif re.search(r"\[THINK_MORE\]", raw, re.IGNORECASE):
        tag = "THINK_MORE"

    # Extract winning thought
    wt_match = re.search(
        r"WINNING THOUGHT:\s*(.+?)(?=\nTRANSITION:|\nRATIONALE:|$)",
        raw,
        re.IGNORECASE | re.DOTALL,
    )
    if wt_match:
        winning = wt_match.group(1).strip()
    else:
        # Fallback: pick the highest-scoring candidate by position in raw text
        winning = candidates[0] if candidates else raw.strip()

    return winning, tag

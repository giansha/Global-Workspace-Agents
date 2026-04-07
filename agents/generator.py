"""
Generator Node — "Divergent Engine" in GWT (§3.6).

Generates N distinct candidate thoughts at dynamic temperature T_gen,
which is regulated by the entropy-based intrinsic drive (§3.3).
"""
from __future__ import annotations

import re
from typing import List

from .base import BaseAgent


def _build_system_directive(N: int) -> str:
    return (
        "I act as the Generator Node, serving as the divergent reasoning engine. "
        "My parameter is to formulate multiple distinct hypotheses to address the "
        "current computational state. "
        f"I must generate exactly {N} distinct candidate thoughts. "
        "I will format my output strictly as a structured numbered list: "
        "'1. [thought]', '2. [thought]', etc. "
        "Each candidate must be substantively different from the others. "
        "No meta-commentary outside the numbered list."
    )


class GeneratorNode(BaseAgent):
    """Produces N divergent candidate thoughts at a dynamically set temperature."""

    def run(self, state_string: str, T_gen: float, N: int) -> List[str]:
        """
        Parameters
        ----------
        state_string:  Full S_t = STM ∪ INPUT ∪ RAG context.
        T_gen:         Dynamic temperature from EntropyDrive.
        N:             Number of candidates to generate.

        Returns
        -------
        List of N candidate thought strings.
        """
        user_content = (
            f"Global State (S_t):\n{state_string}\n\n"
            "I will now generate the numbered candidate thoughts."
        )
        raw = self.call(
            system_directive=_build_system_directive(N),
            user_content=user_content,
            temperature=min(max(T_gen, 0.0), 2.0),
            max_tokens=1024,
        )
        return _parse_candidates(raw, N)


def _parse_candidates(raw: str, N: int) -> List[str]:
    """Extract numbered candidates from model output."""
    candidates: List[str] = []
    # Match lines starting with a number
    pattern = re.compile(r"^\s*(\d+)[.)]\s+(.+)", re.MULTILINE)
    for match in pattern.finditer(raw):
        candidates.append(match.group(2).strip())
    if not candidates:
        # Fallback: split by double newline
        candidates = [p.strip() for p in raw.strip().split("\n\n") if p.strip()]
    # Pad or trim to exactly N
    while len(candidates) < N:
        candidates.append(candidates[-1] if candidates else raw.strip())
    return candidates[:N]

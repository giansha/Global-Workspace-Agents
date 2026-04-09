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
        f"Consider the situation from {N} distinct angles. For each angle, articulate "
        "the core insight or response impulse in 1-3 sentences. Think freely — "
        "contrasting or even contradictory perspectives are valuable. "
        "Output as a numbered list. No meta-commentary."
    )


class GeneratorNode(BaseAgent):
    """Produces N divergent candidate thoughts at a dynamically set temperature."""

    def run(self, state_string: str, T_gen: float, N: int, debug_callback=None, max_tokens: int = 1024) -> List[str]:
        """
        Parameters
        ----------
        state_string:    Full S_t = STM ∪ INPUT ∪ RAG context.
        T_gen:           Dynamic temperature from EntropyDrive.
        N:               Number of candidates to generate.
        debug_callback:  Optional callable(token: str) for streaming debug output.

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
            max_tokens=max_tokens,
            token_callback=debug_callback,
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

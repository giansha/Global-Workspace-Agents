"""
Generator Node — "Divergent Engine" in GWT (§3.6).

Generates N distinct candidate thoughts at dynamic temperature T_gen,
which is regulated by the entropy-based intrinsic drive (§3.3).
"""
from __future__ import annotations

import re
from typing import List

from .base import BaseAgent


def _build_system_directive(N: int, mode: str = "RESPONDING") -> str:
    if mode == "IDLE":
        return (
            f"You are present in this situation right now. Generate {N} distinct thoughts — "
            "what you notice, what you're drawn to, what you're wondering, what you might say. "
            "At least one thought should involve the person nearby, if there is one: "
            "whether to speak, what to ask, what the silence feels like. "
            "Each thought must be self-contained and genuinely felt, not analytical. "
            "Contrasting or even contradictory thoughts are valuable. "
            "Output as a numbered list. No meta-commentary."
        )
    return (
        f"Consider the situation from {N} distinct angles, each angle's content must be self-contained. "
        "Think freely — "
        "contrasting or even contradictory perspectives are valuable. "
        "Output as a numbered list. No meta-commentary."
    )


class GeneratorNode(BaseAgent):
    """Produces N divergent candidate thoughts at a dynamically set temperature."""

    def run(self, state_string: str, T_gen: float, N: int, mode: str = "RESPONDING", debug_callback=None, max_tokens: int = 1024) -> List[str]:
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
            f"Current context: \n{state_string}\n\n"
            "I will now generate the numbered candidate thoughts."
        )
        raw = self.call(
            system_directive=_build_system_directive(N, mode),
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

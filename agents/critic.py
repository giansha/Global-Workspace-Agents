"""
Critic Node — "Convergent Filter" in GWT (§3.6).

Reviews each Generator candidate for logical coherence, safety, and empirical
feasibility. Provides concise critiques without scalar scoring.
Operates at near-zero temperature for deterministic evaluation.
"""
from __future__ import annotations

import re
from typing import List

from .base import BaseAgent

_SYSTEM_DIRECTIVE = (
    "Review each perspective below. For each, give a 1-2 sentence honest assessment: "
    "what rings true, what feels off, what's missing.\n"
    "Format: N. Critique: [text]"
)


class CriticNode(BaseAgent):
    """Evaluates Generator candidates and returns critique strings."""

    def run(
        self,
        state_string: str,
        candidates: List[str],
        temperature: float = 0.3,
        debug_callback=None,
        max_tokens: int = 1024,
    ) -> List[str]:
        """
        Returns
        -------
        List of critique strings, one per candidate.
        """
        numbered = "\n".join(f"{i+1}. {c}" for i, c in enumerate(candidates))
        user_content = (
            f"Current context: \n{state_string}\n\n"
            f"Perspectives to evaluate:\n{numbered}\n\n"
            "Evaluate each one now."
        )
        raw = self.call(
            system_directive=_SYSTEM_DIRECTIVE,
            user_content=user_content,
            temperature=temperature,
            max_tokens=max_tokens,
            token_callback=debug_callback,
        )
        self.last_raw = raw
        return _parse_evaluations(raw, len(candidates))


def _parse_evaluations(raw: str, N: int) -> List[str]:
    """Parse 'N. Critique: ...' lines from model output."""
    results: List[str] = []
    pattern = re.compile(
        r"(?:^|\n)\s*\d+[.)]\s*Critique:\s*(.+)",
        re.IGNORECASE,
    )
    for match in pattern.finditer(raw):
        results.append(match.group(1).strip())
    # Pad if needed
    while len(results) < N:
        results.append("Evaluation unavailable.")
    return results[:N]

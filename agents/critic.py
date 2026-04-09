"""
Critic Node — "Convergent Filter" in GWT (§3.6).

Reviews each Generator candidate for logical coherence, safety, and empirical
feasibility. Assigns scalar scores ∈ [-5, +5] and concise critiques.
Operates at near-zero temperature for deterministic evaluation.
"""
from __future__ import annotations

import re
from typing import List, Tuple

from .base import BaseAgent

_SYSTEM_DIRECTIVE = (
    "I act as the Critic Node, functioning as the strict logical verification filter. "
    "I will receive a discrete numbered list of candidate thoughts. "
    "I am mandated to review each thought for logical coherence, safety, and empirical feasibility. "
    "For each hypothesis, I will assign a scalar feasibility score from -5 (critically flawed) "
    "to +5 (highly actionable), accompanied by a concise critique of 1-2 sentences. "
    "I must output in this exact format for each item:\n"
    "N. Score: [integer from -5 to +5] | Critique: [text]\n"
    "I am restricted from formulating novel hypotheses."
)


class CriticNode(BaseAgent):
    """Evaluates Generator candidates and returns (score, critique) pairs."""

    def run(
        self,
        state_string: str,
        candidates: List[str],
        temperature: float = 0.1,
        debug_callback=None,
        max_tokens: int = 1024,
    ) -> List[Tuple[int, str]]:
        """
        Returns
        -------
        List of (score, critique) tuples, one per candidate.
        """
        numbered = "\n".join(f"{i+1}. {c}" for i, c in enumerate(candidates))
        user_content = (
            f"Global State (S_t):\n{state_string}\n\n"
            f"Hypotheses for Verification:\n{numbered}\n\n"
            "I will now execute my numbered critical evaluation."
        )
        raw = self.call(
            system_directive=_SYSTEM_DIRECTIVE,
            user_content=user_content,
            temperature=temperature,
            max_tokens=max_tokens,
            token_callback=debug_callback,
        )
        return _parse_evaluations(raw, len(candidates))


def _parse_evaluations(raw: str, N: int) -> List[Tuple[int, str]]:
    """Parse 'N. Score: X | Critique: ...' lines from model output."""
    results: List[Tuple[int, str]] = []
    score_pattern = re.compile(
        r"(?:^|\n)\s*\d+[.)]\s*Score:\s*([+-]?\d+)\s*\|?\s*Critique:\s*(.+)",
        re.IGNORECASE,
    )
    for match in score_pattern.finditer(raw):
        score = max(-5, min(5, int(match.group(1))))
        critique = match.group(2).strip()
        results.append((score, critique))
    # Fallback: try to find any score mentions
    if not results:
        score_only = re.compile(r"([+-]?\d+)\s*/\s*5|score[:\s]+([+-]?\d+)", re.IGNORECASE)
        for match in score_only.finditer(raw):
            val = match.group(1) or match.group(2)
            results.append((max(-5, min(5, int(val))), "See full output."))
    # Pad if needed
    while len(results) < N:
        results.append((0, "Evaluation unavailable."))
    return results[:N]

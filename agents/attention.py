"""
Attention Node — "The Spotlight" in GWT (§3.6).

Given the current context and input, identifies 1-3 things worth recalling
from memory to inform the cognitive cycle.
"""
from __future__ import annotations

import re
from typing import List

from .base import BaseAgent

_SYSTEM_DIRECTIVE = (
    "Given the current context and the incoming input, identify at most 2 specific "
    "facts, preferences, or prior decisions worth recalling from long-term memory. "
    "Each query must be a concrete, answerable question or a precise factual phrase — "
    "NOT a vague topic or general subject area. "
    "If nothing specific is worth recalling, output only: none\n"
    "Otherwise output only the recall targets, one per line, numbered. No commentary."
)


class AttentionNode(BaseAgent):
    """Generates RAG retrieval queries from the current cognitive context."""

    def run(self, stm_context: str, current_input: str, debug_callback=None, max_tokens: int = 256) -> List[str]:
        """
        Returns a list of 1–3 retrieval queries.

        Parameters
        ----------
        stm_context:      Formatted STM string (recent cognitive history).
        current_input:    The unresolved external trigger INPUT_t.
        debug_callback:   Optional callable(token: str) for streaming debug output.
        """
        user_content = (
            f"Immediate Context:\n{stm_context}\n\n"
            f"External Environmental Input:\n{current_input}\n\n"
            "I will now synthesize the retrieval queries."
        )
        raw = self.call(
            system_directive=_SYSTEM_DIRECTIVE,
            user_content=user_content,
            temperature=0.3,
            max_tokens=max_tokens,
            token_callback=debug_callback,
        )
        return _parse_queries(raw)


def _parse_queries(raw: str) -> List[str]:
    """Extract numbered query lines from the model output."""
    queries: List[str] = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # Strip leading numbering like "1.", "1)", "-", "•"
        cleaned = re.sub(r"^[\d]+[.)]\s*|^[-•]\s*", "", line).strip()
        if cleaned:
            queries.append(cleaned)
    # If model replied "none", return empty list (no retrieval needed)
    if not queries or (len(queries) == 1 and queries[0].lower() == "none"):
        return []
    return queries[:2]

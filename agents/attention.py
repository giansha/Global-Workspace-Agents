"""
Attention Node — "The Spotlight" in GWT (§3.6).

Parses STM and external input to generate 1-3 precise retrieval queries
for the LTM vector archive. Restricted from engaging the user directly.
"""
from __future__ import annotations

import re
from typing import List

from .base import BaseAgent

_SYSTEM_DIRECTIVE = (
    "I act as the Attention Node. My functional parameter is to parse the "
    "immediate memory state and generate precise search queries to retrieve "
    "contextual data from the long-term vector archive. "
    "I am restricted from engaging the external user directly. "
    "I must output exactly 1 to 3 concise retrieval queries, one per line, "
    "prefixed with a number and a period (e.g. '1. query text'). "
    "No additional commentary."
)


class AttentionNode(BaseAgent):
    """Generates RAG retrieval queries from the current cognitive context."""

    def run(self, stm_context: str, current_input: str) -> List[str]:
        """
        Returns a list of 1–3 retrieval queries.

        Parameters
        ----------
        stm_context:    Formatted STM string (recent cognitive history).
        current_input:  The unresolved external trigger INPUT_t.
        """
        user_content = (
            f"Immediate Context (STM):\n{stm_context}\n\n"
            f"External Environmental Input:\n{current_input}\n\n"
            "I will now synthesize the retrieval queries."
        )
        raw = self.call(
            system_directive=_SYSTEM_DIRECTIVE,
            user_content=user_content,
            temperature=0.3,
            max_tokens=256,
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
    return queries[:3] or [raw.strip()[:200]]

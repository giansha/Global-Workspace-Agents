"""
Short-Term Memory (STM) — the "Stage" in GWT.

Maintains a token-counted sequence of cognitive entries (thoughts, inputs,
resolved interactions). When token count exceeds threshold θ, the engine
triggers memory bifurcation (see engine.py).
"""
from __future__ import annotations

from typing import List, Dict, Any

import tiktoken

GENESIS_STATE = (
    "I am present and ready. Nothing has happened yet — I am simply here, waiting "
    "to think."
)

_ENCODER = tiktoken.get_encoding("cl100k_base")


def _count_tokens(text: str) -> int:
    return len(_ENCODER.encode(text))


class ShortTermMemory:
    """Active, high-speed cache for the current cognitive trajectory."""

    def __init__(self) -> None:
        self._entries: List[Dict[str, Any]] = []
        self._cached_token_count: int = 0
        # Seed STM_0 with the Genesis State (§3.2)
        self.append(role="system", content=GENESIS_STATE, tick=0)

    # ── Public API ────────────────────────────────────────────────────────────

    def append(self, role: str, content: str, tick: int = -1) -> None:
        self._entries.append({"role": role, "content": content, "tick": tick})
        self._cached_token_count += _count_tokens(content)

    def token_count(self) -> int:
        return self._cached_token_count

    def get_context_string(self) -> str:
        """Return a formatted string representation of the full STM for agents."""
        lines: List[str] = []
        for e in self._entries:
            lines.append(f"{e['role'].upper()}: {e['content']}")
        return "\n".join(lines)

    def compress(self, summary: str) -> None:
        """
        Memory bifurcation — semantic summarization branch (§3.5).
        Replaces the verbose history with a dense summary, preserving continuity.
        """
        last_tick = self._entries[-1]["tick"] if self._entries else 0
        compressed_content = f"\n{summary}"
        self._entries = [
            {"role": "memory", "content": compressed_content, "tick": last_tick}
        ]
        self._cached_token_count = _count_tokens(compressed_content)

    def get_all_entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

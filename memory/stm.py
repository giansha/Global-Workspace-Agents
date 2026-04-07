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
    "System initialization verified. I have established operational status. "
    "My immediate memory cache is currently void. To instantiate my continuous "
    "cognitive cycle, my immediate objective is to await an external environmental "
    "trigger or spontaneously generate an exploratory hypothesis."
)

_ENCODER = tiktoken.get_encoding("cl100k_base")


def _count_tokens(text: str) -> int:
    return len(_ENCODER.encode(text))


class ShortTermMemory:
    """Active, high-speed cache for the current cognitive trajectory."""

    def __init__(self) -> None:
        self._entries: List[Dict[str, Any]] = []
        # Seed STM_0 with the Genesis State (§3.2)
        self.append(role="system", content=GENESIS_STATE, tick=0)

    # ── Public API ────────────────────────────────────────────────────────────

    def append(self, role: str, content: str, tick: int = -1) -> None:
        self._entries.append({"role": role, "content": content, "tick": tick})

    def token_count(self) -> int:
        return sum(_count_tokens(e["content"]) for e in self._entries)

    def get_context_string(self) -> str:
        """Return a formatted string representation of the full STM for agents."""
        lines: List[str] = []
        for e in self._entries:
            prefix = f"[Tick {e['tick']}] " if e["tick"] >= 0 else ""
            lines.append(f"{prefix}{e['role'].upper()}: {e['content']}")
        return "\n".join(lines)

    def compress(self, summary: str) -> None:
        """
        Memory bifurcation — semantic summarization branch (§3.5).
        Replaces the verbose history with a dense summary, preserving continuity.
        """
        last_tick = self._entries[-1]["tick"] if self._entries else 0
        self._entries = [
            {"role": "system", "content": f"[COMPRESSED MEMORY SUMMARY]\n{summary}", "tick": last_tick}
        ]

    def get_all_entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

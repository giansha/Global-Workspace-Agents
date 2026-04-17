"""
Short-Term Memory (STM) — the "Stage" in GWT.

Maintains a token-counted sequence of cognitive entries (thoughts, inputs,
resolved interactions). When token count exceeds threshold θ, the engine
triggers memory bifurcation (see engine.py).
"""
from __future__ import annotations

import random
from typing import List, Dict, Any

import tiktoken

_GENESIS_STATES = [
    (   "memory:\n"
        "OK so — café. Afternoon. About 20 seats, maybe 12 people here. "
        "Espresso machine just went off behind the bar. My coffee's been "
        "sitting here a while, getting cold."
    ),
    (   "memory:\n"
        "Bookshop. Small one, single floor. Late afternoon. It started "
        "raining about half an hour ago — still going. Shelves everywhere, "
        "floor to ceiling on three walls, more in the middle. Staff member "
        "at the counter up front, reading. Four other people browsing. "
        "I'm near the back."
    ),
    (   "memory:\n"
        "Library reading room, early evening. Lights dimmed a bit. Closes "
        "in about 30 minutes. Most tables empty — six people left, scattered "
        "around. A librarian is putting books back near the reference section. "
        "Pretty quiet — just the occasional chair scrape or page turn."
    ),
    (   "memory:\n"
        "Late night. 24-hour convenience store. Fluorescent lights, one near "
        "the door flickering on and off. Scanner beeping at the counter every "
        "8-10 seconds — one cashier. Three aisles. Outside: parking lot, two "
        "cars, nobody in them. I'm near the back."
    ),
    (   "memory:\n"
        "Dusk. Sitting outside on a waterfront promenade. Sun's getting low, "
        "everything going orange. Cool out, light breeze off the water. I can "
        "hear the water from here, maybe 30 meters away, but can't really "
        "see it well from this angle. A couple joggers went by a few minutes "
        "ago. Someone's reading on a bench about 10 meters to my left."
    ),
    (   "memory:\n"
        "Late evening. Open-plan office, maybe 40 desks. Only three of us "
        "still here, me included. Main lights are off — just desk lamps and "
        "screen glow at the other two spots. HVAC humming away. Someone left "
        "a half-eaten sandwich on the desk by the window, been there for "
        "hours."
    ),
]


def _pick_genesis() -> str:
    return random.choice(_GENESIS_STATES)

_ENCODER = tiktoken.get_encoding("cl100k_base")


def _count_tokens(text: str) -> int:
    return len(_ENCODER.encode(text))


class ShortTermMemory:
    """Active, high-speed cache for the current cognitive trajectory."""

    def __init__(self) -> None:
        self._entries: List[Dict[str, Any]] = []
        self._cached_token_count: int = 0
        # Seed STM_0 with the Genesis State (§3.2)
        self.append(role="system", content=_pick_genesis(), tick=0)

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

    def snapshot(self) -> tuple[int, int]:
        """Return a lightweight (entry_count, cached_tokens) snapshot for rollback."""
        return len(self._entries), self._cached_token_count

    def rollback_to(self, entry_count: int, cached_tokens: int) -> None:
        """Undo appends back to a prior snapshot (used for IDLE tick cancellation)."""
        if entry_count < len(self._entries):
            self._entries = self._entries[:entry_count]
            self._cached_token_count = cached_tokens

    def get_all_entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

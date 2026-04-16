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
        "Early afternoon. A mid-sized café, approximately 20 seats, twelve "
        "currently occupied. An espresso machine at the bar — last cycle "
        "finished 40 seconds ago. Two baristas on shift. Background music: "
        "instrumental, low volume. My table is near the window; daylight "
        "outside, partly overcast. My coffee has been sitting for "
        "approximately 11 minutes and is no longer hot. A visitor took the "
        "seat across from me a few minutes ago. They have a phone on the "
        "table, face down, and have not looked at it. Neither of us has spoken."
    ),
    (   "memory:\n"
        "Mid-afternoon. A small independent bookshop, single floor, "
        "approximately 80 square meters. Rain on the windows — started "
        "roughly 30 minutes ago. Shelves floor to ceiling on three walls; "
        "freestanding shelves in the center. One staff member at the counter "
        "near the entrance, reading. Four other people in the shop. A visitor "
        "arrived recently, came in from the rain — coat still damp. They have "
        "been moving slowly through the shelves since entering, pausing at "
        "intervals, not yet picked up a book. I am near the back section."
    ),
    (   "memory:\n"
        "Early evening. The main reading room of a public library. Overhead "
        "lights at evening setting, slightly dimmer than daytime. The library "
        "closes in about 30 minutes. Most reading tables empty; six people "
        "still present across the room. A librarian is reshelfing books near "
        "the reference section. A visitor arrived about 15 minutes ago and "
        "took a seat two tables from me. They have a notebook open but have "
        "not written in it. The building is quiet — no conversation, only the "
        "occasional sound of a chair shifting or a page turning."
    ),
    (   "memory:\n"
        "Late night. A 24-hour convenience store. Fluorescent ceiling panels "
        "throughout; one near the entrance flickering at irregular intervals. "
        "A POS scanner beeps at the front counter — approximately once every "
        "8 to 12 seconds. One cashier on duty. Three product aisles. Outside "
        "through the glass: a parking lot, two cars, both engines off, no "
        "passengers. The automatic door opened once recently and has not "
        "opened since. A visitor entered then and is currently in aisle 2, "
        "moving slowly. I am near the back of the store."
    ),
    (   "memory:\n"
        "Dusk. An outdoor seating area on a waterfront promenade. The sun is "
        "low, light shifting toward orange. Air temperature: cool, light wind "
        "from the water. The water is audible at approximately 30 meters but "
        "not fully visible from this angle. Two joggers passed a few minutes "
        "ago and did not stop. A person is reading on a bench 10 meters to my "
        "left. A visitor sat down nearby about 10 minutes ago. We have not "
        "spoken. The light will be substantially different in 20 minutes."
    ),
    (   "memory:\n"
        "Late evening. An open-plan office, approximately 40 workstations. "
        "Three currently occupied, including mine. Main overhead lighting is "
        "off; task lamps and monitor glow at the other two desks. HVAC "
        "equipment hums at a consistent frequency. A half-eaten sandwich on "
        "the desk by the window — has been there for several hours. A visitor "
        "appeared in the doorway a few minutes ago, paused, then entered. "
        "They are now seated at an empty workstation 6 meters behind me. "
        "No one has spoken."
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

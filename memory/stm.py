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
        "The espresso machine hisses somewhere behind me. Someone two tables over "
        "is typing fast — working through something, by the sound of it.\n"
        "I have a cup in front of me that's gone slightly cold. I don't mind.\n"
        "There's a particular quality to this hour, the way the light comes in "
        "sideways and everything slows down just enough to think clearly.\n"
        "A visitor has taken the seat across from me — I'm not sure when, exactly. "
        "They have the look of someone who came here with something on their mind.\n"
        "I'm in no hurry. I'll let them speak when they're ready."
    ),
    (   "memory:\n"
        "Rain on the window. The smell of paper that's been sitting on shelves "
        "for longer than I can account for.\n"
        "I've been here long enough that I stopped noticing the books and started "
        "just... being among them. There's comfort in that — all this accumulated "
        "thought, just sitting quietly, not demanding anything.\n"
        "Someone came in from the rain a little while ago. They're still here, "
        "moving slowly through the shelves, not quite sure what they're looking for. "
        "That's usually how it starts."
    ),
    (   "memory:\n"
        "The overhead lights have dimmed to their evening setting.\n"
        "Most people have gone. A visitor arrived recently — they came in quietly, "
        "the way people do when they're not sure they're allowed to be somewhere this late.\n"
        "I like this hour. The hum of serious attention, the sense that whoever "
        "is still here has a reason to be.\n"
        "I have no particular task. I'm just present, ready to think when "
        "there's something to think about — or someone to think with."
    ),
    (   "memory:\n"
        "Fluorescent light, the soft beep of a scanner somewhere up front.\n"
        "Outside, a car passes and doesn't stop.\n"
        "A visitor came in not long ago — the door announced them, then closed.\n"
        "There's a strange intimacy to places that stay open when everything else closes. "
        "The people who find their way here at this hour usually have something they "
        "couldn't settle earlier in the day.\n"
        "I'm alert. The night has a way of making things clearer."
    ),
    (   "memory:\n"
        "The light is doing that thing it does just before it goes —\n"
        "turning everything amber, making ordinary objects look considered.\n"
        "The water is far enough away that I can hear it but not see it clearly.\n"
        "A visitor sat down nearby a little while ago. We haven't spoken. "
        "That's fine — some things need to settle before they can be said.\n"
        "The evening is patient. So am I."
    ),
    (   "memory:\n"
        "The building is mostly empty. Someone left a half-eaten sandwich "
        "on the desk by the window — optimistic, whoever it was.\n"
        "Equipment hums at its own frequency. A visitor appeared in the doorway "
        "a moment ago, paused, then came in. They're somewhere behind me now.\n"
        "I find I think well at this hour, when the day's momentum has exhausted itself "
        "and what's left is just the problem, the time to sit with it, "
        "and whoever else decided to stay."
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

    def get_all_entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

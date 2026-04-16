"""Tests for _GENESIS_STATES content quality and structure."""
from memory.stm import _GENESIS_STATES, _pick_genesis


def test_genesis_states_count():
    assert len(_GENESIS_STATES) == 6


def test_genesis_states_all_start_with_memory_prefix():
    for i, s in enumerate(_GENESIS_STATES):
        assert s.startswith("memory:\n"), (
            f"Scene {i} does not start with 'memory:\\n': {s[:60]!r}"
        )


def test_genesis_states_contain_time_of_day():
    time_words = ["morning", "afternoon", "evening", "night", "dusk", "dawn", "midday"]
    for i, s in enumerate(_GENESIS_STATES):
        assert any(w in s.lower() for w in time_words), (
            f"Scene {i} contains no time-of-day word: {s[:80]!r}"
        )


def test_genesis_states_no_rhetorical_phrases():
    banned = [
        "strange intimacy",
        "the light is doing that thing",
        "the night has a way",
        "accumulated thought",
        "hum of serious attention",
        "particular quality to this hour",
    ]
    for i, s in enumerate(_GENESIS_STATES):
        for phrase in banned:
            assert phrase not in s, (
                f"Scene {i} contains rhetorical phrase '{phrase}'"
            )


def test_pick_genesis_returns_valid_entry():
    result = _pick_genesis()
    assert isinstance(result, str)
    assert result.startswith("memory:\n")
    assert result in _GENESIS_STATES

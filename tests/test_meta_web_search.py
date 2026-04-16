# tests/test_meta_web_search.py
from agents.meta import _parse_meta_output

def test_parse_web_search_tag():
    raw = (
        'WINNING THOUGHT: "!!2!!"\n'
        'TRANSITION: "[WEB_SEARCH]"\n'
        'RATIONALE: Need current data on this topic.'
    )
    candidates = ["thought one", "thought two", "thought three"]
    thought, tag = _parse_meta_output(raw, candidates)
    assert tag == "WEB_SEARCH"
    assert thought == "thought two"

def test_parse_web_search_tag_case_insensitive():
    raw = 'WINNING THOUGHT: "!!1!!"\nTRANSITION: "[web_search]"\nRATIONALE: need info'
    candidates = ["only thought"]
    _, tag = _parse_meta_output(raw, candidates)
    assert tag == "WEB_SEARCH"

def test_parse_still_handles_think_more():
    raw = 'WINNING THOUGHT: "!!1!!"\nTRANSITION: "[THINK_MORE]"\nRATIONALE: not ready'
    candidates = ["a thought"]
    _, tag = _parse_meta_output(raw, candidates)
    assert tag == "THINK_MORE"

def test_parse_still_handles_response():
    raw = 'WINNING THOUGHT: "!!1!!"\nTRANSITION: "[RESPONSE]"\nRATIONALE: ready'
    candidates = ["a thought"]
    _, tag = _parse_meta_output(raw, candidates)
    assert tag == "RESPONSE"

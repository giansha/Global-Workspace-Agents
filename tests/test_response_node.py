"""Tests for ResponseNode structure and directive content."""
from agents.response import ResponseNode, _SYSTEM_DIRECTIVE

def test_response_directive_has_no_reasoning_exposure():
    banned = ["winning thought", "W_t", "hypothesis", "candidate", "Node"]
    for term in banned:
        assert term.lower() not in _SYSTEM_DIRECTIVE.lower(), \
            f"Response directive exposes internals: '{term}'"

def test_response_directive_instructs_direct_speech():
    assert "speak" in _SYSTEM_DIRECTIVE or "respond" in _SYSTEM_DIRECTIVE
    assert "voice" in _SYSTEM_DIRECTIVE

def test_response_node_is_importable():
    # Smoke test: class exists and accepts expected kwargs
    import inspect
    sig = inspect.signature(ResponseNode.run)
    params = list(sig.parameters.keys())
    assert "winning_thought" in params
    assert "stm_context" in params

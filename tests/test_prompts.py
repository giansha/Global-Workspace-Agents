"""Tests that agent directives are free of architecture meta-language."""
from agents.base import P_SELF
from agents.attention import _SYSTEM_DIRECTIVE as ATTENTION_DIRECTIVE
from agents.generator import _build_system_directive
from agents.critic import _SYSTEM_DIRECTIVE as CRITIC_DIRECTIVE
from agents.meta import _SYSTEM_DIRECTIVE as META_DIRECTIVE

BANNED_TERMS = [
    "cognitive entity",
    "distributed",
    "specialized operational roles",
    "autonomous, continuously executing",
]

def test_p_self_has_no_architecture_terms():
    for term in BANNED_TERMS:
        assert term not in P_SELF, f"P_SELF contains banned term: '{term}'"

def test_p_self_expresses_identity():
    assert "curious" in P_SELF or "curiosity" in P_SELF
    assert "honest" in P_SELF
    assert "perspective" in P_SELF

ATTENTION_BANNED = ["Attention Node", "functional parameter", "vector archive", "restricted from"]

def test_attention_directive_is_task_pure():
    for term in ATTENTION_BANNED:
        assert term not in ATTENTION_DIRECTIVE, f"Attention directive contains: '{term}'"

def test_attention_directive_describes_recall():
    assert "recall" in ATTENTION_DIRECTIVE or "recalling" in ATTENTION_DIRECTIVE

GENERATOR_BANNED = ["Generator Node", "divergent reasoning engine", "computational state", "hypotheses"]

def test_generator_directive_is_task_pure():
    directive = _build_system_directive(3)
    for term in GENERATOR_BANNED:
        assert term not in directive, f"Generator directive contains: '{term}'"

def test_generator_directive_describes_angles():
    directive = _build_system_directive(3)
    assert "angle" in directive or "angles" in directive
    assert "3" in directive

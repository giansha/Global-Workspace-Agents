from config import GWAConfig


def test_new_fields_exist_and_default_to_empty():
    cfg = GWAConfig(low_level_model="", high_level_model="")
    assert cfg.low_level_model == ""
    assert cfg.high_level_model == ""


def test_resolved_low_model_falls_back_to_chat_model():
    cfg = GWAConfig(chat_model="gpt-4o", low_level_model="", high_level_model="")
    assert cfg.resolved_low_model == "gpt-4o"


def test_resolved_high_model_falls_back_to_chat_model():
    cfg = GWAConfig(chat_model="gpt-4o", low_level_model="", high_level_model="")
    assert cfg.resolved_high_model == "gpt-4o"


def test_resolved_low_model_uses_explicit_value():
    cfg = GWAConfig(chat_model="fallback", low_level_model="gpt-4o-mini", high_level_model="")
    assert cfg.resolved_low_model == "gpt-4o-mini"


def test_resolved_high_model_uses_explicit_value():
    cfg = GWAConfig(chat_model="fallback", low_level_model="", high_level_model="gpt-4o")
    assert cfg.resolved_high_model == "gpt-4o"


def test_both_tiers_explicit():
    cfg = GWAConfig(chat_model="fallback", low_level_model="gpt-4o-mini", high_level_model="gpt-4o")
    assert cfg.resolved_low_model == "gpt-4o-mini"
    assert cfg.resolved_high_model == "gpt-4o"

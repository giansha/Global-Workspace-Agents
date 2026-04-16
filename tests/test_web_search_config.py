# tests/test_web_search_config.py
from config import GWAConfig

def test_config_has_tavily_api_key():
    cfg = GWAConfig()
    assert hasattr(cfg, "tavily_api_key")
    assert isinstance(cfg.tavily_api_key, str)

def test_config_has_web_search_max_results():
    cfg = GWAConfig()
    assert hasattr(cfg, "web_search_max_results")
    assert cfg.web_search_max_results == 3

def test_config_tavily_key_from_env(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-abc123")
    cfg = GWAConfig()
    assert cfg.tavily_api_key == "tvly-abc123"

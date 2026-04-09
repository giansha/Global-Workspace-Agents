from config import GWAConfig
from server import ConfigPayload

def test_gwaconfig_idle_defaults():
    cfg = GWAConfig()
    assert cfg.idle_interval == 30.0
    assert cfg.idle_enabled is False

def test_config_payload_idle_fields():
    payload = ConfigPayload()
    assert payload.idle_interval == 30.0
    assert payload.idle_enabled is False

def test_gwaconfig_idle_custom():
    cfg = GWAConfig(idle_interval=10.0, idle_enabled=True)
    assert cfg.idle_interval == 10.0
    assert cfg.idle_enabled is True

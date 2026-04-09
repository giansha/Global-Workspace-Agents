"""Tests that engine wires ResponseNode correctly."""
from unittest.mock import MagicMock, patch
from engine import CognitiveEngine
from config import GWAConfig

def test_config_has_response_max_tokens():
    cfg = GWAConfig()
    assert hasattr(cfg, "response_max_tokens")
    assert isinstance(cfg.response_max_tokens, int)
    assert cfg.response_max_tokens > 0

def test_engine_has_response_node():
    cfg = GWAConfig(api_key="test", api_base_url="http://localhost", chat_model="test")
    with patch("engine.GlobalWorkspace"), \
         patch("engine.AttentionNode"), \
         patch("engine.GeneratorNode"), \
         patch("engine.CriticNode"), \
         patch("engine.MetaNode"), \
         patch("engine.ResponseNode"):
        engine = CognitiveEngine(cfg)
        assert hasattr(engine, "response")

def test_final_response_comes_from_response_node():
    """final_response in TickSnapshot must be the ResponseNode output, not winning_thought."""
    cfg = GWAConfig(api_key="test", api_base_url="http://localhost", chat_model="test", max_ticks=1)

    fake_attention = MagicMock(); fake_attention.run.return_value = ["memory query"]
    fake_generator = MagicMock(); fake_generator.run.return_value = ["internal thought"]
    fake_critic = MagicMock(); fake_critic.run.return_value = [(5, "good")]
    fake_meta = MagicMock(); fake_meta.run.return_value = ("internal thought", "RESPONSE")
    fake_response = MagicMock(); fake_response.run.return_value = "你好！有什么想聊的？"

    with patch("engine.GlobalWorkspace") as MockWS, \
         patch("engine.AttentionNode", return_value=fake_attention), \
         patch("engine.GeneratorNode", return_value=fake_generator), \
         patch("engine.CriticNode", return_value=fake_critic), \
         patch("engine.MetaNode", return_value=fake_meta), \
         patch("engine.ResponseNode", return_value=fake_response):

        mock_ws = MockWS.return_value
        mock_ws.stm.get_context_string.return_value = ""
        mock_ws.stm.token_count.return_value = 0
        mock_ws.build_state_string.return_value = ""
        mock_ws.rag_context = ""
        mock_ws.current_input = "你好"
        mock_ws.tick = 0
        mock_ws.entropy_drive.compute_T_gen.return_value = 0.7
        mock_ws.entropy_drive.last_entropy = 0.5
        mock_ws.entropy_drive.last_T_gen = 0.7
        mock_ws.ltm.retrieve_multi.return_value = ""
        mock_ws.ltm.embed.return_value = [[0.1] * 10]

        engine = CognitiveEngine(cfg)
        snapshots = list(engine.run("你好"))

    assert len(snapshots) == 1
    assert snapshots[0].final_response == "你好！有什么想聊的？"
    assert snapshots[0].final_response != "internal thought"

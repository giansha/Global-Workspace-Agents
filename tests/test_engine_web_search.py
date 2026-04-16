# tests/test_engine_web_search.py
from unittest.mock import MagicMock, patch
from engine import CognitiveEngine
from config import GWAConfig


def _make_mock_ws():
    mock_ws = MagicMock()
    mock_ws.stm.get_context_string.return_value = "STM context"
    mock_ws.stm.token_count.return_value = 0
    mock_ws.stm.snapshot.return_value = (1, 50)
    mock_ws.build_state_string.return_value = "state"
    mock_ws.rag_context = ""
    mock_ws.current_input = "hello"
    mock_ws.tick = 0
    mock_ws.entropy_drive.compute_T_gen.return_value = 0.7
    mock_ws.entropy_drive.last_entropy = 0.5
    mock_ws.entropy_drive.last_T_gen = 0.7
    mock_ws.ltm.retrieve_multi.return_value = ""
    mock_ws.ltm.embed.return_value = [[0.1] * 10]
    mock_ws.last_rag_queries = []
    return mock_ws


def test_engine_web_search_branch():
    """WEB_SEARCH tick: engine calls WebAgent, writes to STM, yields correct snapshot."""
    cfg = GWAConfig(
        api_key="test", api_base_url="http://localhost", chat_model="test",
        max_ticks=2, tavily_api_key="tvly-test", web_search_max_results=3,
    )
    fake_attention = MagicMock(); fake_attention.run.return_value = ["q"]
    fake_generator = MagicMock(); fake_generator.run.return_value = ["a thought"]
    fake_critic = MagicMock(); fake_critic.run.return_value = [(5, "ok")]
    fake_meta = MagicMock()
    fake_meta.run.side_effect = [
        ("a thought", "WEB_SEARCH"),
        ("a thought", "RESPONSE"),
    ]
    fake_response = MagicMock(); fake_response.run.return_value = "final answer"
    fake_web_agent = MagicMock()
    fake_web_agent.formulate_query.return_value = "search query"
    fake_web_agent.synthesize.return_value = "[WEB_SEARCH RESULT]\nsummary"
    raw_results = [{"title": "T", "url": "https://t.com", "content": "C"}]

    with patch("engine.GlobalWorkspace") as MockWS, \
         patch("engine.AttentionNode", return_value=fake_attention), \
         patch("engine.GeneratorNode", return_value=fake_generator), \
         patch("engine.CriticNode", return_value=fake_critic), \
         patch("engine.MetaNode", return_value=fake_meta), \
         patch("engine.ResponseNode", return_value=fake_response), \
         patch("engine.WebAgent", return_value=fake_web_agent), \
         patch("engine.web_search.search", return_value=raw_results) as mock_search:

        MockWS.return_value = _make_mock_ws()
        engine = CognitiveEngine(cfg)
        snapshots = list(engine.run("hello"))

    # First snapshot is WEB_SEARCH
    ws_snap = snapshots[0]
    assert ws_snap.transition_tag == "WEB_SEARCH"
    assert ws_snap.web_search_query == "search query"
    assert ws_snap.web_search_results == "[WEB_SEARCH RESULT]\nsummary"
    assert ws_snap.web_search_raw == raw_results

    # Tavily called with correct args
    mock_search.assert_called_once_with(query="search query", api_key="tvly-test", max_results=3)

    # STM appended with web_search role
    engine.workspace.stm.append.assert_any_call(
        role="web_search",
        content="[WEB_SEARCH RESULT]\nsummary",
        tick=0,
    )

    # Final snapshot is RESPONSE
    assert snapshots[-1].transition_tag == "RESPONSE"
    assert snapshots[-1].final_response == "final answer"


def test_engine_web_search_failure_writes_failed_marker():
    """When Tavily raises, engine writes [WEB_SEARCH FAILED] to STM and continues."""
    cfg = GWAConfig(
        api_key="test", api_base_url="http://localhost", chat_model="test",
        max_ticks=2, tavily_api_key="tvly-bad",
    )
    fake_attention = MagicMock(); fake_attention.run.return_value = ["q"]
    fake_generator = MagicMock(); fake_generator.run.return_value = ["a thought"]
    fake_critic = MagicMock(); fake_critic.run.return_value = [(5, "ok")]
    fake_meta = MagicMock()
    fake_meta.run.side_effect = [
        ("a thought", "WEB_SEARCH"),
        ("a thought", "RESPONSE"),
    ]
    fake_response = MagicMock(); fake_response.run.return_value = "answer"
    fake_web_agent = MagicMock()
    fake_web_agent.formulate_query.return_value = "query"

    with patch("engine.GlobalWorkspace") as MockWS, \
         patch("engine.AttentionNode", return_value=fake_attention), \
         patch("engine.GeneratorNode", return_value=fake_generator), \
         patch("engine.CriticNode", return_value=fake_critic), \
         patch("engine.MetaNode", return_value=fake_meta), \
         patch("engine.ResponseNode", return_value=fake_response), \
         patch("engine.WebAgent", return_value=fake_web_agent), \
         patch("engine.web_search.search", side_effect=Exception("network error")):

        MockWS.return_value = _make_mock_ws()
        engine = CognitiveEngine(cfg)
        snapshots = list(engine.run("hello"))

    engine.workspace.stm.append.assert_any_call(
        role="web_search",
        content="[WEB_SEARCH FAILED]",
        tick=0,
    )
    # Engine recovered and eventually returned RESPONSE
    assert snapshots[-1].transition_tag == "RESPONSE"

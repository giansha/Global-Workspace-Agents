# tests/test_web_agent.py
from unittest.mock import patch, MagicMock

def _make_agent():
    from agents.web_agent import WebAgent
    return WebAgent(api_base_url="http://localhost", api_key="test", model="gpt-mock")

def test_formulate_query_returns_string():
    agent = _make_agent()
    with patch.object(agent, "call", return_value="  latest climate policy 2025  ") as mock_call:
        result = agent.formulate_query(
            winning_thought="I wonder what the latest climate summit decided.",
            stm_context="VISITOR: Tell me about climate change.\nME: I know the basics but need recent data."
        )
    assert result == "latest climate policy 2025"
    mock_call.assert_called_once()
    args, kwargs = mock_call.call_args
    assert "search query" in kwargs.get("system_directive", "").lower() or \
           "search query" in str(args).lower()

def test_synthesize_returns_prefixed_summary():
    agent = _make_agent()
    search_results = [
        {"title": "Climate Deal 2025", "url": "https://news.com/climate", "content": "World leaders agreed to..."},
        {"title": "COP30 Outcome", "url": "https://eco.org/cop30", "content": "Emissions targets were set at..."},
    ]
    with patch.object(agent, "call", return_value="[WEB_SEARCH RESULT]\nLeaders agreed on new emissions targets."):
        result = agent.synthesize(
            winning_thought="I wonder what the latest climate summit decided.",
            search_results=search_results,
        )
    assert result.startswith("[WEB_SEARCH RESULT]")
    assert "emissions" in result.lower() or "Leaders" in result

def test_synthesize_formats_results_for_llm():
    agent = _make_agent()
    search_results = [
        {"title": "T1", "url": "https://u1.com", "content": "C1"},
        {"title": "T2", "url": "https://u2.com", "content": "C2"},
    ]
    with patch.object(agent, "call", return_value="[WEB_SEARCH RESULT]\nsummary") as mock_call:
        agent.synthesize("thought", search_results)
    _, kwargs = mock_call.call_args
    user_content = kwargs.get("user_content", "")
    assert "T1" in user_content and "https://u1.com" in user_content
    assert "T2" in user_content and "https://u2.com" in user_content

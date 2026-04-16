# tests/test_tools_web_search.py
from unittest.mock import MagicMock, patch

def test_search_returns_normalized_list():
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "results": [
            {"title": "Page A", "url": "https://a.com", "content": "Some content about A"},
            {"title": "Page B", "url": "https://b.com", "content": "Some content about B"},
        ]
    }
    with patch("tools.web_search.TavilyClient", return_value=mock_client):
        from tools.web_search import search
        results = search(query="test query", api_key="tvly-fake", max_results=2)

    assert len(results) == 2
    assert results[0] == {"title": "Page A", "url": "https://a.com", "content": "Some content about A"}
    assert results[1]["url"] == "https://b.com"

def test_search_passes_correct_args():
    mock_client = MagicMock()
    mock_client.search.return_value = {"results": []}
    with patch("tools.web_search.TavilyClient", return_value=mock_client) as MockCls:
        from tools.web_search import search
        search(query="climate 2025", api_key="tvly-key", max_results=5)

    MockCls.assert_called_once_with(api_key="tvly-key")
    mock_client.search.assert_called_once_with(query="climate 2025", max_results=5)

def test_search_handles_missing_fields():
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "results": [{"url": "https://x.com"}]   # no title or content
    }
    with patch("tools.web_search.TavilyClient", return_value=mock_client):
        from tools.web_search import search
        results = search(query="q", api_key="k", max_results=1)

    assert results[0]["title"] == ""
    assert results[0]["content"] == ""
    assert results[0]["url"] == "https://x.com"

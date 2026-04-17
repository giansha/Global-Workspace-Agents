"""
tools/web_search.py — Thin Tavily search wrapper.

Returns a normalized list of result dicts so the rest of the system
never depends on the Tavily client directly.
"""
from __future__ import annotations

from tavily import TavilyClient


def search(query: str, api_key: str, max_results: int = 3) -> list[dict]:
    """
    Call Tavily and return normalized results.

    Returns
    -------
    list of {"title": str, "url": str, "content": str}
    Empty list if Tavily returns no results.
    """
    client = TavilyClient(api_key=api_key)
    response = client.search(query=query, max_results=max_results)
    raw = response.get("results", [])
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", ""),
        }
        for r in raw
    ]

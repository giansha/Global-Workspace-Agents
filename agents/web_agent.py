"""
Web Agent — formulates search queries and synthesizes Tavily results.

Uses the low-level model. Two responsibilities:
  1. formulate_query: extract a concise web search query from the current thought
  2. synthesize: summarize raw Tavily results relative to the winning thought
"""
from __future__ import annotations

from typing import List

from .base import BaseAgent

_FORMULATE_DIRECTIVE = (
    "Given the current thought and conversation context, produce a concise, "
    "effective web search query that would retrieve the information needed to "
    "advance the thought.\n\n"
    "Rules:\n"
    "- Output ONLY the search query string — no explanation, no punctuation wrapper\n"
    "- Be specific and factual (names, dates, topics)\n"
    "- Prefer 3–8 words"
)

_SYNTHESIZE_DIRECTIVE = (
    "You are given a thought and a set of web search results. "
    "Synthesize the most relevant facts from the results that help address the thought.\n\n"
    "Rules:\n"
    "- Be concise and factual — 2–5 sentences\n"
    "- Start your response with exactly: [WEB_SEARCH RESULT]\n"
    "- Do not copy-paste URLs or raw text — paraphrase key findings\n"
    "- If results are irrelevant, say so briefly after the prefix"
)


class WebAgent(BaseAgent):
    """Formulates search queries and synthesizes web results for the cognitive engine."""

    def formulate_query(self, winning_thought: str, stm_context: str) -> str:
        """Return a trimmed search query string derived from the winning thought."""
        user_content = (
            f"Current thought:\n{winning_thought}\n\n"
            f"Conversation context:\n{stm_context}"
        )
        raw = self.call(
            system_directive=_FORMULATE_DIRECTIVE,
            user_content=user_content,
            temperature=0.2,
            max_tokens=64,
        )
        return raw.strip()

    def synthesize(self, winning_thought: str, search_results: List[dict]) -> str:
        """Summarize raw Tavily results relative to the winning thought."""
        formatted = "\n\n".join(
            f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
            for r in search_results
        )
        user_content = (
            f"Thought:\n{winning_thought}\n\n"
            f"Search Results:\n{formatted}"
        )
        raw = self.call(
            system_directive=_SYNTHESIZE_DIRECTIVE,
            user_content=user_content,
            temperature=0.3,
            max_tokens=512,
        )
        return raw.strip()

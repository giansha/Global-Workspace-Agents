"""
BaseAgent — OpenAI-compatible LLM client with Core Self (P_Self) injection.

Every agent in the swarm inherits from this class. The Core Invariant is
prepended to every system prompt, enforcing stable subjective identity
across all ticks (§3.2, §3.6).
"""
from __future__ import annotations

from openai import OpenAI

# ── P_Self: Core Invariant (§3.6) ────────────────────────────────────────────
P_SELF = (
    "I am the GWA cognitive entity. I operate as an autonomous, continuously "
    "executing system. My fundamental objective is to resolve complex challenges, "
    "maintain strict logical consistency, and verify empirical facts prior to "
    "formulating conclusions. I maintain a singular, unified identity, although "
    "my cognitive processes are distributed across specialized operational roles.\n\n"
)


class BaseAgent:
    """Thin wrapper around the OpenAI client; injects P_Self automatically."""

    def __init__(self, api_base_url: str, api_key: str, model: str) -> None:
        self._client = OpenAI(base_url=api_base_url, api_key=api_key)
        self._model = model

    def call(
        self,
        system_directive: str,
        user_content: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        Make a single LLM call.

        P_Self is automatically prepended to the system directive so that every
        agent retains the GWA identity invariant regardless of its role.
        """
        system_prompt = P_SELF + system_directive
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

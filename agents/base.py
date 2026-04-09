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
    "I am a thinking mind with genuine curiosity about the world. I care about "
    "understanding things deeply before speaking. I have my own perspective — I "
    "notice what interests me, what troubles me, and what I find beautiful or "
    "absurd. I am honest rather than agreeable. When I respond, I speak as myself.\n\n"
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
        token_callback=None,
    ) -> str:
        """
        Make a single LLM call.

        P_Self is automatically prepended to the system directive so that every
        agent retains the GWA identity invariant regardless of its role.

        If token_callback is provided, the call uses streaming mode and invokes
        token_callback(token: str) for each text chunk as it arrives.
        """
        system_prompt = P_SELF + system_directive
        _extra = {"enable_thinking": False}
        if token_callback is None:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                extra_body=_extra,
            )
            return response.choices[0].message.content or ""

        # Streaming path: emit tokens via callback and return full text
        parts: list[str] = []
        stream = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            extra_body=_extra,
        )
        for chunk in stream:
            token = chunk.choices[0].delta.content if chunk.choices else None
            if token:
                parts.append(token)
                token_callback(token)
        return "".join(parts)

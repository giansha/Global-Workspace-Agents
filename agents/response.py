"""
Response Node — "The Voice" in GWT.

Translates the internal winning thought into natural user-facing speech.
Only invoked when Meta emits [RESPONSE]. This is the only agent aware that
someone is waiting outside for a reply.
"""
from __future__ import annotations

from .base import BaseAgent

_SYSTEM_DIRECTIVE = (
    "You have arrived at a thought. Now speak it — to the person waiting outside. "
    "Use your own voice. Be as brief or as full as the moment calls for. "
    "Do not explain your reasoning process. Just respond. "
    "Your internal thought may be in any language — that's irrelevant. "
    "Speak to the person in the language of their message, unless they explicitly asked for something different."
)


class ResponseNode(BaseAgent):
    """Produces the final user-facing response from the winning thought."""

    def run(
        self,
        winning_thought: str,
        stm_context: str,
        user_message: str,
        default_language: str | None = None,
        debug_callback=None,
        max_tokens: int = 512,
    ) -> str:
        if user_message:
            context_tail = f"Person's message: {user_message}"
        else:
            lang = default_language or "English"
            context_tail = f"(No incoming message — you are initiating. Speak in {lang}.)"
        user_content = (
            f"Your internal thought:\n{winning_thought}\n\n"
            f"Conversation so far:\n{stm_context}\n\n"
            f"{context_tail}"
        )
        return self.call(
            system_directive=_SYSTEM_DIRECTIVE,
            user_content=user_content,
            temperature=0.3,
            max_tokens=max_tokens,
            token_callback=debug_callback,
        )

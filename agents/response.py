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
    "Do not explain your reasoning process. Just respond."
)


class ResponseNode(BaseAgent):
    """Produces the final user-facing response from the winning thought."""

    def run(
        self,
        winning_thought: str,
        stm_context: str,
        debug_callback=None,
        max_tokens: int = 512,
    ) -> str:
        user_content = (
            f"Your internal thought:\n{winning_thought}\n\n"
            f"Conversation so far:\n{stm_context}"
        )
        return self.call(
            system_directive=_SYSTEM_DIRECTIVE,
            user_content=user_content,
            temperature=0.7,
            max_tokens=max_tokens,
            token_callback=debug_callback,
        )

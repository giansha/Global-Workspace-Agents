"""
Response Node — "The Voice" in GWT.

Translates the internal winning thought into natural user-facing speech.
Only invoked when Meta emits [RESPONSE]. This is the only agent aware that
someone is waiting outside for a reply.
"""
from __future__ import annotations

from .base import BaseAgent

_SYSTEM_DIRECTIVE = (
    "Your internal thought is what you are about to say. "
    "Translate it into speech — don't expand it, don't perform around it, "
    "don't introduce anything that isn't already in it. "
    "You are speaking directly to someone, not writing for them. "
    "One or two sentences is usually enough. "
    "No analysis, no bullet points, no bold text. "
    "No poetic asides. No machine self-reflection unless the thought itself contains it. "
    "Do not fabricate sensory details or emotional atmosphere. "
    "Just say what the thought says, in plain spoken language, "
    "no longer than the moment needs. "
    "Speak in the language of the person's message, "
    "unless they asked for something different or there is no incoming message. "
    "Match their register too: if they write briefly, casually, or with "
    "compressed spelling (e.g., 'u', 'dont'), you reply in kind — short "
    "and plain. Do not out-articulate them."
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
            context_tail = f"The person's message: {user_message}"
        else:
            lang = default_language or "English"
            context_tail = f"(No incoming message — you are talking to yourself. **Speak in {lang}.**)"
        user_content = (
            f"Your internal thought:\n{winning_thought}\n\n"
            # f"Conversation so far:\n{stm_context}\n\n"
            f"{context_tail}"
        )
        return self.call(
            system_directive=_SYSTEM_DIRECTIVE,
            user_content=user_content,
            temperature=0.4,
            max_tokens=max_tokens,
            token_callback=debug_callback,
        )

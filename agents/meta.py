"""
Meta Node — "Metacognitive Executive" in GWT (§3.6).

Performs contextual metacognition to select the optimal winning thought W_t
and dictates the state transition tag T_t ∈ {[THINK_MORE], [RESPONSE]}.

Also used for STM compression (summarization) during memory bifurcation (§3.5).
"""
from __future__ import annotations

import re
from typing import List

from .base import BaseAgent

_SYSTEM_DIRECTIVE = (
    "Given these perspectives and their assessments, which feels most true, "
    "complete, and worth expressing? Select it and decide the next action.\n\n"
    "Refer to COGNITIVE STATUS in the context before deciding the transition tag:\n"
    "- If MODE is \"RESPONDING\": the visitor is waiting for a reply. Prefer [RESPONSE] "
    "when the winning thought is complete and directly addresses their need.\n"
    "- If MODE is \"IDLE\": no one is waiting. Check memory — if the last visitor message "
    "carries [RESOLVED], you have already replied to that message; if memory contains "
    "no visitor messages, no one has spoken to you yet. In either sub-case, "
    "you are free to autonomously decide the best next action.\n\n"
    "Transition options:\n"
    "- [RESPONSE]: the winning thought is complete and ready to share with the visitor.\n"
    "- [THINK_MORE]: the thought needs further internal development before responding.\n"
    "- [WEB_SEARCH]: the winning thought requires external real-time information to "
    "proceed (current events, specific data, unknown facts). Do not choose this for "
    "information already present in memory.\n\n"
    "Output format:\n"
    "WINNING THOUGHT: \"!!N!!\", where N is the number of the selected perspective\n"
    "TRANSITION: \"[RESPONSE]\" or \"[THINK_MORE]\" or \"[WEB_SEARCH]\"\n"
    "RATIONALE: [1-2 sentences]"
)

_SUMMARIZE_DIRECTIVE = (
    "Synthesize a dense, coherent summary of the conversation history below. "
    "Preserve all key decisions, unresolved threads, and important conclusions. "
    "It should be substantially shorter than the original while maintaining "
    "full narrative continuity. "
    "Retain greater detail for recent history and progressively compress earlier content. "
    "Output only the summary text."
)

_EXTRACT_KNOWLEDGE_DIRECTIVE = (
    "You are a knowledge extractor. Given a cognitive history, extract the durable "
    "knowledge, experiences, and insights worth remembering long-term. "
    "Focus on:\n"
    "- Established facts and conclusions reached\n"
    "- User preferences, interests, and goals revealed\n"
    "- Unresolved questions or open problems\n"
    "- Key decisions made and their rationale\n\n"
    "Do NOT include transient context, raw conversation turns, or step-by-step "
    "reasoning chains. Output a concise, self-contained knowledge fragment that "
    "would be useful if retrieved months later with no other context. "
    "Output only the knowledge text, no preamble."
)


class MetaNode(BaseAgent):
    """Arbitrates candidates and controls state transition; also handles STM compression."""

    def run(
        self,
        state_string: str,
        candidates: List[str],
        evaluations: List[str],
        debug_callback=None,
        max_tokens: int = 1024,
    ) -> Tuple[str, str]:
        """
        Returns
        -------
        (winning_thought, transition_tag) where tag ∈ {"THINK_MORE", "RESPONSE"}
        """
        numbered_candidates = "\n".join(f"{i+1}. {c}" for i, c in enumerate(candidates))
        numbered_evals = "\n".join(
            f"{i+1}. Critique: {critique}"
            for i, critique in enumerate(evaluations)
        )
        user_content = (
            f"Current context:\n{state_string}\n\n"
            f"Candidate Thoughts:\n{numbered_candidates}\n\n"
            f"Critical Evaluations:\n{numbered_evals}\n\n"
            "I will now execute the final arbitration."
        )
        raw = self.call(
            system_directive=_SYSTEM_DIRECTIVE,
            user_content=user_content,
            temperature=0.3,
            max_tokens=max_tokens,
            token_callback=debug_callback,
        )
        self.last_raw = raw
        return _parse_meta_output(raw, candidates)

    def summarize(self, stm_context: str) -> str:
        """Generate a dense semantic summary for STM compression (§3.5)."""
        raw = self.call(
            system_directive=_SUMMARIZE_DIRECTIVE,
            user_content=f"Cognitive History to Compress:\n{stm_context}",
            temperature=0.3,
            max_tokens=800,
        )
        return raw.strip()

    def extract_knowledge(self, stm_context: str) -> str:
        """Extract durable knowledge fragments from STM history for LTM storage (§3.5)."""
        raw = self.call(
            system_directive=_EXTRACT_KNOWLEDGE_DIRECTIVE,
            user_content=f"Cognitive History:\n{stm_context}",
            temperature=0.2,
            max_tokens=600,# TODO: figure out ideal token limit for this
        )
        return raw.strip()


def _parse_meta_output(raw: str, candidates: List[str]) -> Tuple[str, str]:
    """Extract winning thought and transition tag from Meta output."""
    # Extract tag — check WEB_SEARCH before THINK_MORE to avoid false negatives
    tag = "THINK_MORE"
    if re.search(r"\[RESPONSE\]", raw, re.IGNORECASE):
        tag = "RESPONSE"
    elif re.search(r"\[WEB_SEARCH\]", raw, re.IGNORECASE):
        tag = "WEB_SEARCH"
    elif re.search(r"\[THINK_MORE\]", raw, re.IGNORECASE):
        tag = "THINK_MORE"

    # Extract winning thought by number
    wt_match = re.search(r"\s*!!(\d+)!!", raw, re.IGNORECASE)
    if wt_match:
        idx = int(wt_match.group(1)) - 1
        if 0 <= idx < len(candidates):
            winning = candidates[idx]
        else:
            winning = candidates[0] if candidates else raw.strip()
    else:
        winning = candidates[0] if candidates else raw.strip()

    return winning, tag

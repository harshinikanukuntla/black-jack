"""Turns the human player's free text into a hit or stand decision.

This lets you type naturally ("deal me the next card", "I'll stand pat")
instead of a fixed command. It's just keyword matching, no LLM call, since
this needs to be instant and never fail. Stand words are checked first
because a phrase like "no more" would otherwise get caught by the "more"
hit-keyword.
"""

from __future__ import annotations

STAND_WORDS = (
    "stand", "stay", "pass", "hold", "done", "enough", "no more",
    "stop", "no thanks", "i'm good", "im good",
)
HIT_WORDS = (
    "hit", "deal", "draw", "another", "more", "again", "next card",
    "yes", "sure", "give me",
)
# A bare "no" only counts as stand when it's the whole message. As a
# substring it's too easy to misfire on something like "no worries, hit me".
EXACT_STAND_WORDS = {"no", "nope", "nah", "n"}


def parse_intent(text: str) -> str | None:
    """Return "hit", "stand", or None if the input couldn't be classified."""
    lowered = text.lower().strip()
    if not lowered:
        return None
    if lowered in EXACT_STAND_WORDS:
        return "stand"
    if any(word in lowered for word in STAND_WORDS):
        return "stand"
    if any(word in lowered for word in HIT_WORDS):
        return "hit"
    return None

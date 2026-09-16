"""Tiny natural-language intent parsing for the human player's turn.

Keeps the human interaction free-text ("deal me the next card", "I'll stand
pat") without requiring an LLM round-trip just to parse hit/stand — that
would add latency and a failure mode to the most latency-sensitive part of
the game. Stand-ish words are checked first since phrases like "no more"
would otherwise trip the "more" hit-keyword.
"""

from __future__ import annotations

STAND_WORDS = (
    "stand", "stay", "pass", "hold", "done", "enough", "no more",
    "stop", "i'm good", "im good", "no thanks",
)
HIT_WORDS = (
    "hit", "deal", "draw", "another", "more", "again", "next card",
    "yes", "sure", "go", "give me",
)


def parse_intent(text: str) -> str | None:
    """Return "hit", "stand", or None if the input couldn't be classified."""
    lowered = text.lower().strip()
    if not lowered:
        return None
    if any(word in lowered for word in STAND_WORDS):
        return "stand"
    if any(word in lowered for word in HIT_WORDS):
        return "hit"
    return None

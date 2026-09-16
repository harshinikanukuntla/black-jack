"""Card drawing primitive.

Per the assignment spec, this simulates a "card" as a random value between
2 and 11 (inclusive) rather than modeling a full 52-card deck. Only the
Dealer is allowed to call this — players must ask the dealer to draw on
their behalf.
"""

import random


def draw_card() -> int:
    """Return a random card value between 2 and 11 inclusive."""
    return random.randint(2, 11)

"""The card drawing function given by the assignment.

A "card" here is just a random number from 2 to 11, not a real deck.
Only the Dealer calls this. Every player has to go through the dealer.
"""

import random


def draw_card() -> int:
    """Return a random card value between 2 and 11 inclusive."""
    return random.randint(2, 11)

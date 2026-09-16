"""The AI dealer agent.

The dealer is the only agent allowed to draw cards. Every player (human or
AI) must ask the dealer to draw a card for them rather than calling the
card-drawing function directly.
"""

from __future__ import annotations

import time

from cards import draw_card


class Dealer:
    """The single AI dealer that services draw requests from all players."""

    def __init__(self, name: str = "Dealer", *, think_time: float = 0.0) -> None:
        self.name = name
        self._think_time = think_time

    def draw_for(self, player_name: str) -> int:
        """Draw a card on behalf of ``player_name`` and announce it."""
        print(f'{self.name}: "{player_name}, here comes your card..."')
        if self._think_time:
            time.sleep(self._think_time)
        card = draw_card()
        print(f"{self.name}: dealt a {card} to {player_name}.")
        return card

    def announce_round_start(self, player_names: list[str]) -> None:
        roster = ", ".join(player_names)
        print(f'{self.name}: "Welcome, everyone. Today\'s table: {roster}. '
              f'Each of you may draw up to three cards. Just ask me when '
              f'you\'re ready — let\'s begin!"')

    def announce_turn(self, player_name: str) -> None:
        print(f'\n{self.name}: "{player_name}, you\'re up."')

    def announce_result(self, message: str) -> None:
        print(f"{self.name}: {message}")

    def decide_own_play(self, total: int, cards_drawn: int, max_cards: int) -> str:
        """Fixed dealer rule: hit while total < 17, else stand.

        Unlike the AI agents, the dealer's own hand follows the standard,
        transparent blackjack convention rather than a personality/LLM
        brain — real dealers play by fixed rules, not judgment calls.
        """
        if cards_drawn >= max_cards or total >= 17:
            return "stand"
        return "hit"

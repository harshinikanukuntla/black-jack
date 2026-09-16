"""The AI dealer agent.

The dealer is the only one allowed to draw cards. Every player, human or
AI, has to ask the dealer to draw a card for them instead of calling
draw_card() themselves.
"""

from __future__ import annotations

from cards import draw_card


class Dealer:
    """The single AI dealer that services draw requests from all players."""

    def __init__(self, name: str = "Dealer") -> None:
        self.name = name

    def draw_for(self, player_name: str) -> int:
        """Draw a card on behalf of ``player_name`` and announce it."""
        print(f'  {self.name}: "{player_name}, here comes your card..."')
        card = draw_card()
        print(f"  {self.name}: dealt a {card} to {player_name}.")
        return card

    def announce_round_start(self, player_names: list[str]) -> None:
        roster = ", ".join(player_names)
        print(f'{self.name}: "Welcome, everyone. Today\'s table: {roster}. '
              f'Each of you may draw up to three cards. Just ask me when '
              f'you\'re ready, let\'s begin!"')

    def announce_turn(self, player_name: str) -> None:
        print(f'\n{self.name}: "{player_name}, you\'re up."')

    def announce_result(self, message: str) -> None:
        print(f"{self.name}: {message}")

    def decide_own_play(self, total: int) -> str:
        """Fixed dealer rule: hit while total is under 17, else stand.

        Unlike the AI agents, the dealer's own hand follows the standard,
        fixed blackjack rule rather than a personality or LLM brain. Real
        dealers play by a published rule, not judgment, so the game's
        outcome can't be second-guessed as biased for or against the house.
        """
        return "hit" if total < 17 else "stand"

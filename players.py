"""Player types: the human, AI agents, and the dealer's own hand.

No player ever draws its own card directly. Every draw goes through the
Dealer (see dealer.py), which is the only thing allowed to call
draw_card().
"""

from __future__ import annotations

from dataclasses import dataclass, field

from brains import Brain
from nlp import parse_intent

MAX_CARDS = 3


@dataclass
class Player:
    """Common state shared by every hand at the table."""

    name: str
    hand: list[int] = field(default_factory=list)
    standing: bool = False

    @property
    def total(self) -> int:
        return sum(self.hand)

    @property
    def cards_drawn(self) -> int:
        return len(self.hand)

    @property
    def busted(self) -> bool:
        return self.total > 21

    @property
    def can_draw(self) -> bool:
        # A total of exactly 21 can't be improved, only risked, so nobody
        # (human included) gets asked to draw again once they hit it.
        return (
            not self.busted
            and not self.standing
            and self.total < 21
            and self.cards_drawn < MAX_CARDS
        )

    def add_card(self, card: int) -> None:
        self.hand.append(card)
        if self.cards_drawn >= MAX_CARDS or self.total >= 21:
            self.standing = True

    def status_line(self) -> str:
        hand_str = ", ".join(str(c) for c in self.hand) or "(no cards yet)"
        state = "BUST" if self.busted else ("stood" if self.standing else "playing")
        return f"{self.name}: [{hand_str}] = {self.total} ({state})"


class HumanPlayer(Player):
    """The user, who chooses hit/stand via natural-language terminal input."""

    def ask_decision(self) -> str:
        while True:
            remaining = MAX_CARDS - self.cards_drawn
            card_word = "card" if remaining == 1 else "cards"
            prompt = f"  Your total is {self.total} ({remaining} {card_word} left you could draw). Hit or stand? > "
            raw = input(prompt).strip()
            intent = parse_intent(raw)
            if intent is not None:
                return intent
            print("  (Didn't catch that. Please try things like 'hit me', "
                  "'deal me another card', or 'I'll stand'.)")


class AIPlayer(Player):
    """An AI agent whose hit/stand choice is delegated to a Brain."""

    def __init__(self, name: str, brain: Brain) -> None:
        super().__init__(name=name)
        self.brain = brain

    def decide(self) -> str:
        return self.brain.decide(self.name, list(self.hand), self.total, self.cards_drawn, MAX_CARDS)

    def comment(self, decision: str) -> str:
        return self.brain.comment(self.name, decision, self.total)

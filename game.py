"""The game loop.

This is the only place that enforces the actual rules: turn order, the
three-card cap, bust detection, and who wins. Brains (heuristic or LLM)
only ever get asked for a single hit or stand choice, and only when
Player.can_draw says a real choice exists. They never get to bend a rule.
"""

from __future__ import annotations

from brains import build_brain, personality_for_index
from dealer import Dealer
from players import AIPlayer, HumanPlayer, Player


class Game:
    def __init__(self, human_name: str = "You", num_agents: int = 3,
                 use_llm: bool = True, model: str = "llama3.1:8b",
                 base_url: str = "http://localhost:11434") -> None:
        self.dealer = Dealer()
        self.human = HumanPlayer(name=human_name)
        self.agents: list[AIPlayer] = [
            AIPlayer(
                name=personality_for_index(i).name,
                brain=build_brain(personality_for_index(i), use_llm, model, base_url),
            )
            for i in range(num_agents)
        ]
        self.dealer_hand = Player(name=self.dealer.name)

    @property
    def players(self) -> list[Player]:
        """Every hand that competes for the win, in turn order (dealer last)."""
        return [self.human, *self.agents, self.dealer_hand]

    def run(self) -> None:
        print("=" * 60)
        print("  SIMPLIFIED BLACKJACK: you vs. the AI agents vs. the dealer")
        print("=" * 60)
        self.dealer.announce_round_start([self.human.name, *[a.name for a in self.agents]])

        self._take_turn(self.human)
        for agent in self.agents:
            self._take_turn(agent)
        self._take_dealer_turn()

        self._show_final_table()
        self._announce_winner()

    def _take_turn(self, player: Player) -> None:
        """Run one player's turn: keep asking for a decision until they stop drawing."""
        self.dealer.announce_turn(player.name)
        while player.can_draw:
            if isinstance(player, HumanPlayer):
                decision = player.ask_decision()
            else:
                decision = player.decide()
                print(f'  {player.name}: "{player.comment(decision)}"')

            if decision == "stand":
                player.standing = True
                break

            self._draw_and_report(player)

        if not player.busted:
            print(f"  {player.name} finishes with {player.total}.")

    def _take_dealer_turn(self) -> None:
        """The dealer's own hand: no personality, just the fixed hit-under-17 rule."""
        self.dealer.announce_turn(self.dealer_hand.name)
        while self.dealer_hand.can_draw:
            if self.dealer.decide_own_play(self.dealer_hand.total) == "stand":
                self.dealer_hand.standing = True
                break
            self._draw_and_report(self.dealer_hand)

        if not self.dealer_hand.busted:
            print(f"  {self.dealer_hand.name} finishes with {self.dealer_hand.total}.")

    def _draw_and_report(self, player: Player) -> None:
        """Ask the dealer for one card, add it to the hand, and print what happened."""
        card = self.dealer.draw_for(player.name)
        player.add_card(card)
        print(f"  -> {player.status_line()}")
        if player.busted:
            print(f"  {player.name} busts!")

    def _show_final_table(self) -> None:
        print("\n" + "-" * 60)
        print("FINAL TABLE")
        print("-" * 60)
        for player in self.players:
            print(" " + player.status_line())

    def _announce_winner(self) -> None:
        contenders = [p for p in self.players if not p.busted]
        if not contenders:
            self.dealer.announce_result("Everyone busted. No winner this round!")
            return

        best_total = max(p.total for p in contenders)
        winners = [p for p in contenders if p.total == best_total]

        if len(winners) == 1:
            self.dealer.announce_result(f"{winners[0].name} wins with {best_total}!")
        else:
            names = " and ".join(p.name for p in winners)
            self.dealer.announce_result(f"It's a tie between {names}, both at {best_total}!")

import contextlib
import io
import unittest
from unittest.mock import patch

from dealer import Dealer
from game import Game
from players import Player


class TestDealerOwnPlay(unittest.TestCase):
    def test_hits_below_17(self) -> None:
        dealer = Dealer()
        self.assertEqual(dealer.decide_own_play(total=10, cards_drawn=1, max_cards=3), "hit")

    def test_stands_at_or_above_17(self) -> None:
        dealer = Dealer()
        self.assertEqual(dealer.decide_own_play(total=17, cards_drawn=2, max_cards=3), "stand")

    def test_forced_stand_at_max_cards(self) -> None:
        dealer = Dealer()
        self.assertEqual(dealer.decide_own_play(total=10, cards_drawn=3, max_cards=3), "stand")


class TestAnnounceWinner(unittest.TestCase):
    def _game(self) -> Game:
        return Game(human_name="You", num_agents=3, use_llm=False)

    def test_single_winner(self) -> None:
        game = self._game()
        game.human.hand = [10, 9]  # 19
        game.agents[0].hand = [10, 5]  # 15
        game.agents[1].hand = [5, 5]  # 10, bust-free but low
        game.agents[2].hand = [11, 11, 5]  # 27, bust
        game.dealer_hand.hand = [10, 6]  # 16

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            game._announce_winner()
        self.assertIn("You wins with 19", buf.getvalue())

    def test_tie_between_two_players(self) -> None:
        game = self._game()
        game.human.hand = [10, 10]  # 20
        game.agents[0].hand = [10, 10]  # 20
        game.agents[1].hand = [5, 5]
        game.agents[2].hand = [5, 5]
        game.dealer_hand.hand = [5, 5]

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            game._announce_winner()
        output = buf.getvalue()
        self.assertIn("tie", output.lower())
        self.assertIn("20", output)

    def test_everyone_busts_means_no_winner(self) -> None:
        game = self._game()
        for player in game.players:
            player.hand = [11, 11, 11]  # 33, bust

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            game._announce_winner()
        self.assertIn("no winner", buf.getvalue().lower())


class TestFullGameSmoke(unittest.TestCase):
    def test_full_game_runs_with_scripted_human_input(self) -> None:
        game = Game(human_name="Tester", num_agents=3, use_llm=False)
        buf = io.StringIO()
        # Human always hits until forced to stop; AI agents/dealer use the
        # deterministic heuristic brain, so this exercises the entire loop
        # without needing a live LLM.
        with patch("builtins.input", return_value="hit"), contextlib.redirect_stdout(buf):
            game.run()
        output = buf.getvalue()
        self.assertIn("FINAL TABLE", output)
        self.assertTrue(
            "wins with" in output or "tie" in output.lower() or "no winner" in output.lower()
        )


if __name__ == "__main__":
    unittest.main()

import unittest

from players import MAX_CARDS, Player


class TestPlayer(unittest.TestCase):
    def test_starts_empty(self) -> None:
        p = Player(name="Test")
        self.assertEqual(p.total, 0)
        self.assertEqual(p.cards_drawn, 0)
        self.assertFalse(p.busted)
        self.assertTrue(p.can_draw)

    def test_bust_detected_over_21(self) -> None:
        p = Player(name="Test")
        p.add_card(11)
        p.add_card(11)
        self.assertEqual(p.total, 22)
        self.assertTrue(p.busted)
        self.assertFalse(p.can_draw)

    def test_cannot_draw_more_than_max_cards(self) -> None:
        p = Player(name="Test")
        for _ in range(MAX_CARDS):
            self.assertTrue(p.can_draw)
            p.add_card(2)
        self.assertFalse(p.can_draw)
        self.assertEqual(p.cards_drawn, MAX_CARDS)
        self.assertTrue(p.standing)  # forced stand once the cap is hit

    def test_standing_prevents_further_draws(self) -> None:
        p = Player(name="Test")
        p.add_card(5)
        p.standing = True
        self.assertFalse(p.can_draw)

    def test_cannot_draw_once_total_is_21(self) -> None:
        # A total of exactly 21 can only get worse, never better, so this
        # should stop the turn even with cards and draws still available.
        p = Player(name="Test")
        p.add_card(10)
        p.add_card(11)
        self.assertEqual(p.total, 21)
        self.assertFalse(p.busted)
        self.assertFalse(p.can_draw)
        self.assertTrue(p.standing)

    def test_status_line_reports_state(self) -> None:
        p = Player(name="Test")
        self.assertIn("playing", p.status_line())
        p.add_card(11)
        p.add_card(11)
        self.assertIn("BUST", p.status_line())


if __name__ == "__main__":
    unittest.main()

import unittest

from brains import DEFAULT_PERSONALITIES, HeuristicBrain, personality_for_index


class TestHeuristicBrain(unittest.TestCase):
    # Stopping at the card cap or at a total of 21 is Player.can_draw's job
    # (see test_players.py), not the brain's, since decide() only ever gets
    # called when a real choice still exists.

    def test_hits_below_threshold(self) -> None:
        brain = HeuristicBrain(risk_tolerance=0)  # threshold 16
        self.assertEqual(brain.decide("A", [5], 5, 1, 3), "hit")

    def test_stands_above_threshold(self) -> None:
        brain = HeuristicBrain(risk_tolerance=0)
        self.assertEqual(brain.decide("A", [10, 9], 19, 2, 3), "stand")

    def test_cautious_stands_earlier_than_aggressive(self) -> None:
        cautious = HeuristicBrain(risk_tolerance=-3)  # threshold 13
        aggressive = HeuristicBrain(risk_tolerance=3)  # threshold 19
        self.assertEqual(cautious.decide("A", [7, 7], 14, 2, 3), "stand")
        self.assertEqual(aggressive.decide("A", [7, 7], 14, 2, 3), "hit")

    def test_comment_mentions_total(self) -> None:
        brain = HeuristicBrain()
        comment = brain.comment("A", "hit", 12)
        self.assertIn("12", comment)


class TestPersonalities(unittest.TestCase):
    def test_cycles_when_more_agents_than_presets(self) -> None:
        n = len(DEFAULT_PERSONALITIES)
        wrapped = personality_for_index(n)
        self.assertIn(DEFAULT_PERSONALITIES[0].name, wrapped.name)
        self.assertNotEqual(wrapped.name, DEFAULT_PERSONALITIES[0].name)

    def test_first_agents_use_presets_directly(self) -> None:
        for i, preset in enumerate(DEFAULT_PERSONALITIES):
            self.assertEqual(personality_for_index(i).name, preset.name)


if __name__ == "__main__":
    unittest.main()

import unittest

from nlp import parse_intent


class TestParseIntent(unittest.TestCase):
    def test_hit_phrases(self) -> None:
        for phrase in ["hit", "hit me", "deal me the next card", "give me another", "draw"]:
            self.assertEqual(parse_intent(phrase), "hit", phrase)

    def test_stand_phrases(self) -> None:
        for phrase in ["stand", "I'll stand", "stay", "no more", "I'm good", "pass"]:
            self.assertEqual(parse_intent(phrase), "stand", phrase)

    def test_bare_no_means_stand(self) -> None:
        for phrase in ["no", "No", "nope", "nah", "n"]:
            self.assertEqual(parse_intent(phrase), "stand", phrase)

    def test_unrecognized_returns_none(self) -> None:
        self.assertIsNone(parse_intent("what's the weather"))
        self.assertIsNone(parse_intent(""))

    def test_good_alone_is_not_mistaken_for_hit(self) -> None:
        # "good" used to false-match the old "go" hit-keyword.
        self.assertIsNone(parse_intent("good"))

    def test_no_as_a_substring_does_not_override_a_clear_hit(self) -> None:
        # A bare "no" means stand, but "no" buried in a sentence that's
        # clearly asking to hit shouldn't get overridden by it.
        self.assertEqual(parse_intent("no worries, hit me"), "hit")

    def test_stand_takes_priority_over_hit_keyword_collision(self) -> None:
        # "no more" contains "more" (a hit keyword) but should read as stand.
        self.assertEqual(parse_intent("no more for me"), "stand")


if __name__ == "__main__":
    unittest.main()

import unittest

from cards import draw_card


class TestDrawCard(unittest.TestCase):
    def test_range_is_2_to_11_inclusive(self) -> None:
        seen = {draw_card() for _ in range(2000)}
        self.assertTrue(seen.issubset(set(range(2, 12))))
        self.assertGreaterEqual(min(seen), 2)
        self.assertLessEqual(max(seen), 11)

    def test_returns_an_int(self) -> None:
        self.assertIsInstance(draw_card(), int)


if __name__ == "__main__":
    unittest.main()

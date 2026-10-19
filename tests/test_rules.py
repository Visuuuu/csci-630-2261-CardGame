import unittest
from uno_game.card import Card, Color, CardType
from uno_game.rules import (
    is_playable,
    get_playable_cards,
    is_valid_color_choice,
)

class TestUNORules(unittest.TestCase):
    def setUp(self):
        self.top_card = Card(
            Color.RED, CardType.NUMBER, 5
        )
        self.active_color = Color.RED

    def test_same_color(self):
        card = Card(Color.RED, CardType.NUMBER, 9)
        self.assertTrue(
            is_playable(
                card, self.top_card, self.active_color
            )
        )

    def test_same_number(self):
        card = Card(Color.BLUE, CardType.NUMBER, 5)
        self.assertTrue(
            is_playable(
                card, self.top_card, self.active_color
            )
        )

    def test_different_color_and_number(self):
        card = Card(Color.GREEN, CardType.NUMBER, 7)
        self.assertFalse(
            is_playable(
                card, self.top_card, self.active_color
            )
        )

    def test_same_color_action(self):
        card = Card(Color.RED, CardType.SKIP)
        self.assertTrue(
            is_playable(
                card, self.top_card, self.active_color
            )
        )

    def test_same_action_type(self):
        top_card = Card(Color.BLUE, CardType.SKIP)
        card = Card(Color.GREEN, CardType.SKIP)
        self.assertTrue(
            is_playable(card, top_card, Color.BLUE)
        )

    def test_different_action_type(self):
        top_card = Card(Color.BLUE, CardType.SKIP)
        card = Card(Color.GREEN, CardType.REVERSE)
        self.assertFalse(
            is_playable(card, top_card, Color.BLUE)
        )

    def test_wild_always_playable(self):
        card = Card(Color.WILD, CardType.WILD)
        self.assertTrue(
            is_playable(
                card, self.top_card, self.active_color
            )
        )

    def test_active_color_after_wild(self):
        top_card = Card(Color.WILD, CardType.WILD)
        blue_card = Card(Color.BLUE, CardType.NUMBER, 3)
        red_card = Card(Color.RED, CardType.NUMBER, 3)
        self.assertTrue(
            is_playable(blue_card, top_card, Color.BLUE)
        )
        self.assertFalse(
            is_playable(red_card, top_card, Color.BLUE)
        )

    def test_get_playable_cards(self):
        red_seven = Card(Color.RED, CardType.NUMBER, 7)
        blue_five = Card(Color.BLUE, CardType.NUMBER, 5)
        green_nine = Card(Color.GREEN, CardType.NUMBER, 9)
        wild = Card(Color.WILD, CardType.WILD)
        hand = (red_seven, blue_five, green_nine, wild)
        legal_cards = get_playable_cards(
            hand, self.top_card, self.active_color
        )
        self.assertEqual(
            legal_cards,
            [red_seven, blue_five, wild],
        )

    def test_no_playable_cards(self):
        hand = (
            Card(Color.GREEN, CardType.NUMBER, 2),
            Card(Color.YELLOW, CardType.NUMBER, 8),
        )
        self.assertEqual(
            get_playable_cards(
                hand, self.top_card, self.active_color
            ),
            [],
        )

    def test_valid_wild_color_choice(self):
        for color in (Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE):
            self.assertTrue(is_valid_color_choice(color))
        self.assertFalse(
            is_valid_color_choice(Color.WILD)
        )

    def test_invalid_active_color(self):
        card = Card(Color.RED, CardType.NUMBER, 7)
        with self.assertRaises(ValueError):
            is_playable(
                card, self.top_card, Color.WILD
            )

if __name__ == "__main__":
    unittest.main()

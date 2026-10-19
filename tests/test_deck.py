import unittest
from collections import Counter
from uno_game.card import Card, Color, CardType
from uno_game.deck import Deck

class TestDeck(unittest.TestCase):
    def setUp(self):
        self.deck = Deck(seed=42)

    def test_initial_deck_size(self):
        self.assertEqual(
            self.deck.remaining_cards(), 104
        )

    def test_card_distribution(self):
        counts = Counter(
            (card.color, card.card_type, card.number)
            for card in self.deck.cards
        )
        for color in [
            Color.RED,
            Color.YELLOW,
            Color.GREEN,
            Color.BLUE,
        ]:
            self.assertEqual(
                counts[(color, CardType.NUMBER, 0)], 1
            )
            for number in range(1, 10):
                self.assertEqual(
                    counts[(color, CardType.NUMBER, number)], 2
                )
            for action in [
                CardType.SKIP,
                CardType.REVERSE,
                CardType.DRAW_TWO,
            ]:
                self.assertEqual(
                    counts[(color, action, None)], 2
                )
        self.assertEqual(
            counts[(Color.WILD, CardType.WILD, None)], 4
        )

    def test_draw_card(self):
        card = self.deck.draw()
        self.assertIsInstance(card, Card)
        self.assertEqual(
            self.deck.remaining_cards(), 103
        )

    def test_seed_reproducibility(self):
        another_deck = Deck(seed=42)
        self.assertEqual(
            self.deck.cards, another_deck.cards
        )

    def test_empty_deck(self):
        for _ in range(104):
            self.deck.draw()
        self.assertTrue(self.deck.is_empty())
        with self.assertRaises(ValueError):
            self.deck.draw()


if __name__ == "__main__":
    unittest.main()

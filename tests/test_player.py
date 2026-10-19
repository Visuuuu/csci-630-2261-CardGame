import unittest
from uno_game.card import Card, Color, CardType
from uno_game.deck import Deck
from uno_game.player import Player


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player(0, "Test Player")
        self.deck = Deck(seed=42)

    def test_player_starts_empty(self):
        self.assertEqual(self.player.hand_size(), 0)
        self.assertEqual(self.player.hand_points(), 0)

    def test_receive_card(self):
        card = Card(Color.RED, CardType.NUMBER, 5)
        self.player.receive_card(card)
        self.assertEqual(self.player.hand_size(), 1)
        self.assertIn(card, self.player.hand)

    def test_draw_seven_cards(self):
        self.player.draw_cards(self.deck, 7)
        self.assertEqual(self.player.hand_size(), 7)
        self.assertEqual(
            self.deck.remaining_cards(), 97
        )

    def test_play_card(self):
        card = Card(Color.BLUE, CardType.SKIP)
        self.player.receive_card(card)
        played = self.player.play_card(card)
        self.assertEqual(played, card)
        self.assertEqual(self.player.hand_size(), 0)

    def test_cannot_play_missing_card(self):
        card = Card(Color.RED, CardType.NUMBER, 8)
        with self.assertRaises(ValueError):
            self.player.play_card(card)

    def test_hand_points(self):
        self.player.receive_card(
            Card(Color.RED, CardType.NUMBER, 5)
        )
        self.player.receive_card(
            Card(Color.BLUE, CardType.SKIP)
        )
        self.player.receive_card(
            Card(Color.WILD, CardType.WILD)
        )
        self.assertEqual(self.player.hand_points(), 75)

    def test_uno_detection(self):
        self.player.receive_card(
            Card(Color.GREEN, CardType.NUMBER, 3)
        )
        self.assertTrue(self.player.has_uno())
        self.player.receive_card(
            Card(Color.YELLOW, CardType.NUMBER, 7)
        )
        self.assertFalse(self.player.has_uno())

    def test_win_detection(self):
        card = Card(Color.RED, CardType.NUMBER, 2)
        self.player.receive_card(card)
        self.assertFalse(self.player.has_won())
        self.player.play_card(card)
        self.assertTrue(self.player.has_won())

    def test_hand_cannot_be_modified_directly(self):
        card = Card(Color.RED, CardType.NUMBER, 4)
        self.player.receive_card(card)
        with self.assertRaises(AttributeError):
            self.player.hand.append(card)

    def test_invalid_player_id(self):
        with self.assertRaises(ValueError):
            Player(-1, "Invalid Player")

    def test_negative_draw_count(self):
        with self.assertRaises(ValueError):
            self.player.draw_cards(self.deck, -1)


if __name__ == "__main__":
    unittest.main()

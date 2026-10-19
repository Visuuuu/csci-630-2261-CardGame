import unittest
from uno_game.card import Card, Color, CardType
from uno_game.game import UNOGame

class TestUNOTurns(unittest.TestCase):
    def setUp(self):
        self.game = UNOGame(
            ["P0", "P1", "P2", "P3"],
            seed=42,
        )

    def prepare_card(self, card):
        """Give P0 a legal card for testing."""
        self.game.current_player.receive_card(card)
        self.game.active_color = card.color

    def test_play_number_card(self):
        card = Card(Color.RED, CardType.NUMBER, 7)
        self.prepare_card(card)
        old_size = self.game.players[0].hand_size()
        self.game.play_turn(card)
        self.assertEqual(
            self.game.players[0].hand_size(),
            old_size - 1,
        )
        self.assertEqual(self.game.top_card, card)
        self.assertEqual(self.game.current_player_index, 1)

    def test_illegal_card_rejected(self):
        card = Card(Color.GREEN, CardType.NUMBER, 3)
        self.game.current_player.receive_card(card)
        self.game.active_color = Color.RED
        self.game.discard_pile.append(
            Card(Color.RED, CardType.NUMBER, 8)
        )
        with self.assertRaises(ValueError):
            self.game.play_turn(card)
        self.assertEqual(self.game.current_player_index, 0)
        self.assertEqual(self.game.turn_count, 0)

    def test_skip_card(self):
        card = Card(Color.RED, CardType.SKIP)
        self.prepare_card(card)
        self.game.play_turn(card)
        self.assertEqual(self.game.current_player_index, 2)

    def test_reverse_card(self):
        card = Card(Color.BLUE, CardType.REVERSE)
        self.prepare_card(card)
        self.game.play_turn(card)
        self.assertEqual(self.game.direction, -1)
        self.assertEqual(self.game.current_player_index, 3)

    def test_draw_two_card(self):
        card = Card(Color.YELLOW, CardType.DRAW_TWO)
        self.prepare_card(card)
        old_size = self.game.players[1].hand_size()
        self.game.play_turn(card)
        self.assertEqual(
            self.game.players[1].hand_size(),
            old_size + 2,
        )
        self.assertEqual(self.game.current_player_index, 2)

    def test_wild_card(self):
        card = Card(Color.WILD, CardType.WILD)
        self.game.current_player.receive_card(card)
        self.game.play_turn(card, chosen_color=Color.GREEN)
        self.assertEqual(self.game.active_color, Color.GREEN)
        self.assertEqual(self.game.current_player_index, 1)

    def test_wild_requires_color(self):
        card = Card(Color.WILD, CardType.WILD)
        self.game.current_player.receive_card(card)
        with self.assertRaises(ValueError):
            self.game.play_turn(card)
        self.assertIn(card, self.game.current_player.hand)
        self.assertEqual(self.game.turn_count, 0)

    def test_draw_when_no_playable_card(self):
        player = self.game.current_player
        # Arrange a controlled test hand.
        player._hand = [
            Card(Color.GREEN, CardType.NUMBER, 2)
        ]
        self.game.discard_pile.append(
            Card(Color.RED, CardType.NUMBER, 5)
        )
        self.game.active_color = Color.RED
        old_deck_size = self.game.deck.remaining_cards()
        self.game.play_turn()
        self.assertEqual(player.hand_size(), 2)
        self.assertEqual(
            self.game.deck.remaining_cards(),
            old_deck_size - 1,
        )
        self.assertEqual(self.game.current_player_index, 1)

    def test_automatic_uno_announcement(self):
        player = self.game.current_player
        player._hand = [
            Card(Color.RED, CardType.NUMBER, 3),
            Card(Color.RED, CardType.NUMBER, 7),
        ]
        self.game.active_color = Color.RED
        message = self.game.play_turn(player.hand[0])
        self.assertIn("UNO!", message)
        self.assertEqual(player.hand_size(), 1)

    def test_winner_detection(self):
        player = self.game.current_player
        player._hand = [
            Card(Color.RED, CardType.NUMBER, 5)
        ]
        self.game.active_color = Color.RED
        message = self.game.play_turn(player.hand[0])
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, player)
        self.assertIn("wins!", message)

    def test_cannot_play_after_game_over(self):
        self.game.game_over = True
        with self.assertRaises(ValueError):
            self.game.play_turn()

    def test_card_recycling(self):
        game = self.game
        top = game.top_card
        recycled_card = Card(
            Color.BLUE, CardType.NUMBER, 4
        )
        game.discard_pile = [recycled_card, top]
        game.deck.cards.clear()
        game._recycle_discard_pile()
        self.assertEqual(len(game.discard_pile), 1)
        self.assertEqual(game.top_card, top)
        self.assertEqual(game.deck.remaining_cards(), 1)
        self.assertEqual(game.deck.cards[0], recycled_card)

if __name__ == "__main__":
    unittest.main()

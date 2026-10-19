import unittest
from uno_game.card import CardType
from uno_game.game import UNOGame

class TestUNOGameInitialization(unittest.TestCase):
    def setUp(self):
        self.names = [
            "Random Agent",
            "Greedy Agent",
            "Heuristic Agent",
            "Monte Carlo Agent",
        ]
        self.game = UNOGame(self.names, seed=42)

    def test_four_players_created(self):
        self.assertEqual(len(self.game.players), 4)

    def test_player_names(self):
        actual_names = [
            player.name for player in self.game.players
        ]
        self.assertEqual(actual_names, self.names)

    def test_seven_cards_each(self):
        for player in self.game.players:
            self.assertEqual(player.hand_size(), 7)

    def test_starting_discard_card(self):
        self.assertEqual(len(self.game.discard_pile), 1)
        self.assertEqual(
            self.game.top_card.card_type,
            CardType.NUMBER,
        )

    def test_active_color_matches_starting_card(self):
        self.assertEqual(
            self.game.active_color,
            self.game.top_card.color,
        )

    def test_initial_turn_state(self):
        self.assertEqual(self.game.current_player_index, 0)
        self.assertEqual(self.game.direction, 1)
        self.assertFalse(self.game.game_over)
        self.assertIsNone(self.game.winner)

    def test_remaining_deck_size(self):
        self.assertEqual(
            self.game.deck.remaining_cards(), 75
        )

    def test_total_card_conservation(self):
        total = (
            self.game.deck.remaining_cards()
            + len(self.game.discard_pile)
            + sum(
                player.hand_size()
                for player in self.game.players
            )
        )
        self.assertEqual(total, 104)

    def test_next_player_clockwise(self):
        self.assertEqual(
            self.game.get_next_player_index(), 1
        )

    def test_next_player_counterclockwise(self):
        self.game.direction = -1
        self.assertEqual(
            self.game.get_next_player_index(), 3
        )

    def test_reproducible_initial_state(self):
        other_game = UNOGame(self.names, seed=42)
        self.assertEqual(
            self.game.top_card, other_game.top_card
        )
        for first, second in zip(
            self.game.players, other_game.players
        ):
            self.assertEqual(first.hand, second.hand)

    def test_reject_invalid_player_count(self):
        with self.assertRaises(ValueError):
            UNOGame(["Player 1", "Player 2"])

    def test_reject_duplicate_names(self):
        with self.assertRaises(ValueError):
            UNOGame(["A", "A", "B", "C"])

if __name__ == "__main__":
    unittest.main()

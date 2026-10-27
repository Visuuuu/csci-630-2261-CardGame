import unittest
from interface.game_view import (
    card_label,
    color_hex,
    get_game_view,
)
from uno_game.card import Card, CardType, Color
from uno_game.game import UNOGame


class TestGameView(unittest.TestCase):

    def setUp(self):
        self.game = UNOGame(
            ["Random", "Greedy", "Heuristic", "Monte Carlo"],
            seed=42,
        )

    def test_four_players_in_view(self):
        view = get_game_view(self.game)
        self.assertEqual(len(view["players"]), 4)

    def test_hands_hidden_by_default(self):
        view = get_game_view(self.game)
        for player in view["players"]:
            self.assertEqual(
                player["cards"],
                ["UNO"] * 7,
            )

    def test_demo_reveals_hands(self):
        view = get_game_view(
            self.game,
            reveal_hands=True,
        )
        for index, player in enumerate(view["players"]):
            expected = [
                str(card)
                for card in self.game.players[index].hand
            ]
            self.assertEqual(
                player["cards"],
                expected,
            )

    def test_active_color_matches_game(self):
        view = get_game_view(self.game)
        self.assertEqual(
            view["active_color"],
            self.game.active_color.value,
        )
        self.assertEqual(
            view["top_card"],
            str(self.game.top_card),
        )

    def test_current_player_indicator(self):
        view = get_game_view(self.game)
        current = [
            player
            for player in view["players"]
            if player["is_current"]
        ]
        self.assertEqual(len(current), 1)
        self.assertEqual(
            current[0]["player_id"], 0
        )

    def test_winner_display(self):
        self.game.game_over = True
        self.game.winner = self.game.players[2]
        view = get_game_view(self.game)
        self.assertTrue(view["game_over"])
        self.assertEqual(
            view["winner"],
            "Heuristic",
        )
        self.assertIsNone(view["current_player"])

    def test_card_label(self):
        card = Card(
            Color.RED,
            CardType.NUMBER,
            5,
        )
        self.assertEqual(
            card_label(card),
            "Red 5",
        )

    def test_all_colors_have_display_values(self):
        for color in Color:
            value = color_hex(color)
            self.assertTrue(value.startswith("#"))
            self.assertEqual(len(value), 7)


if __name__ == "__main__":
    unittest.main()

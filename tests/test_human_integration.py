import unittest
from agents.human_player import HumanPlayer
from interface.demo_config import create_demo_controller
from uno_game.card import Color


class TestHumanIntegration(unittest.TestCase):
    def make_controller(self, lineup):
        return create_demo_controller(
            agent_types=lineup,
            game_seed=42,
            mc_simulations=5,
            mc_depth=2,
        )

    def test_one_human_three_ai(self):
        controller = self.make_controller([
            "Human",
            "Random",
            "Greedy",
            "Heuristic",
        ])
        self.assertEqual(len(controller.agents), 4)
        self.assertIsInstance(
            controller.agents[0],
            HumanPlayer,
        )
        self.assertTrue(controller.is_human_turn)

    def test_four_human_players(self):
        controller = self.make_controller(
            ["Human"] * 4
        )
        self.assertTrue(
            all(
                isinstance(agent, HumanPlayer)
                for agent in controller.agents
            )
        )

    def test_ai_only_configuration(self):
        controller = self.make_controller([
            "Random",
            "Greedy",
            "Heuristic",
            "Monte Carlo",
        ])
        self.assertFalse(controller.is_human_turn)
        record = controller.step()
        self.assertEqual(record.turn_number, 1)
        self.assertEqual(len(controller.turn_history), 1)

    def test_human_move_updates_history(self):
        controller = self.make_controller(
            ["Human"] * 4
        )
        legal_cards = (
            controller.game.get_current_legal_cards()
        )
        if legal_cards:
            card = legal_cards[0]
            chosen_color = (
                Color.RED
                if card.color == Color.WILD
                else None
            )
        else:
            card = None
            chosen_color = None
        record = controller.submit_human_turn(
            card=card,
            chosen_color=chosen_color,
        )
        self.assertEqual(record.player_id, 0)
        self.assertEqual(record.decision_time_ms, 0.0)
        self.assertEqual(
            len(controller.turn_history),
            1,
        )
        self.assertEqual(
            controller.game.turn_count,
            1,
        )

    def test_ai_cannot_submit_human_move(self):
        controller = self.make_controller([
            "Random",
            "Greedy",
            "Heuristic",
            "Monte Carlo",
        ])
        with self.assertRaises(ValueError):
            controller.submit_human_turn()

    def test_human_turn_cannot_use_ai_step(self):
        controller = self.make_controller(
            ["Human"] * 4
        )
        with self.assertRaises(ValueError):
            controller.step()

    def test_automated_tournament_rejects_humans(self):
        controller = self.make_controller([
            "Human",
            "Random",
            "Greedy",
            "Heuristic",
        ])
        with self.assertRaises(ValueError):
            controller.run_game(verbose=False)

    def test_human_move_advances_game(self):
        controller = self.make_controller(
            ["Human"] * 4
        )
        legal_cards = (
            controller.game.get_current_legal_cards()
        )
        card = legal_cards[0] if legal_cards else None
        chosen_color = (
            Color.BLUE
            if card is not None
            and card.color == Color.WILD
            else None
        )
        controller.submit_human_turn(
            card=card,
            chosen_color=chosen_color,
        )
        self.assertEqual(
            controller.game.turn_count,
            1,
        )
        if not controller.game.game_over:
            self.assertTrue(
                controller.is_human_turn
            )


if __name__ == "__main__":
    unittest.main()

import unittest
from agents.human_player import HumanPlayer
from interface.demo_config import create_demo_controller
from uno_game.card import Color


class TestHumanController(unittest.TestCase):

    def test_mixed_human_and_ai_configuration(self):
        controller = create_demo_controller(
            agent_types=[
                "Human",
                "Random",
                "Greedy",
                "Heuristic",
            ],
            game_seed=42,
        )
        self.assertIsInstance(
            controller.agents[0],
            HumanPlayer,
        )
        self.assertEqual(len(controller.agents), 4)

    def test_four_human_players(self):
        controller = create_demo_controller(
            agent_types=["Human"] * 4,
            game_seed=42,
        )
        self.assertTrue(
            all(
                isinstance(agent, HumanPlayer)
                for agent in controller.agents
            )
        )

    def test_ai_step_rejects_human_turn(self):
        controller = create_demo_controller(
            agent_types=["Human"] * 4,
            game_seed=42,
        )
        with self.assertRaises(ValueError):
            controller.step()

    def test_human_turn_is_recorded(self):
        controller = create_demo_controller(
            agent_types=["Human"] * 4,
            game_seed=42,
        )
        self.assertTrue(controller.is_human_turn)
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
        self.assertEqual(len(controller.turn_history), 1)
        self.assertEqual(controller.game.turn_count, 1)

    def test_automated_game_rejects_humans(self):
        controller = create_demo_controller(
            agent_types=["Human"] * 4,
            game_seed=42,
        )
        with self.assertRaises(ValueError):
            controller.run_game(verbose=False)


if __name__ == "__main__":
    unittest.main()

import unittest
from agents.greedy_agent import GreedyAgent
from agents.heuristic_agent import HeuristicAgent
from agents.monte_carlo_agent import MonteCarloAgent
from agents.monte_carlo_v2_agent import MonteCarloV2Agent
from agents.random_agent import RandomAgent
from interface.demo_config import (
    AGENT_TYPES,
    DEFAULT_LINEUP,
    V1_V2_DEMO_LINEUP,
    create_demo_controller,
)


class TestGUIV2Config(unittest.TestCase):

    def test_five_strategies_available(self):
        self.assertEqual(
            len(AGENT_TYPES),
            5,
        )
        self.assertIn(
            "Monte Carlo V2",
            AGENT_TYPES,
        )

    def test_default_lineup_still_has_four_players(self):
        self.assertEqual(len(DEFAULT_LINEUP), 4)
        controller = create_demo_controller(
            DEFAULT_LINEUP
        )
        self.assertEqual(
            len(controller.agents),
            4,
        )
        self.assertIsInstance(
            controller.agents[3],
            MonteCarloAgent,
        )
        self.assertNotIsInstance(
            controller.agents[3],
            MonteCarloV2Agent,
        )

    def test_preset_contains_both_versions(self):
        self.assertEqual(
            V1_V2_DEMO_LINEUP,
            (
                "Monte Carlo",
                "Monte Carlo V2",
                "Greedy",
                "Heuristic",
            ),
        )

    def test_preset_creates_correct_agents(self):
        controller = create_demo_controller(
            V1_V2_DEMO_LINEUP,
            mc_simulations=5,
            mc_depth=2,
        )
        self.assertIsInstance(
            controller.agents[0],
            MonteCarloAgent,
        )
        self.assertNotIsInstance(
            controller.agents[0],
            MonteCarloV2Agent,
        )
        self.assertIsInstance(
            controller.agents[1],
            MonteCarloV2Agent,
        )
        self.assertIsInstance(
            controller.agents[2],
            GreedyAgent,
        )
        self.assertIsInstance(
            controller.agents[3],
            HeuristicAgent,
        )

    def test_four_v2_agents_allowed(self):
        controller = create_demo_controller(
            ["Monte Carlo V2"] * 4,
            mc_simulations=3,
            mc_depth=2,
        )
        self.assertTrue(
            all(
                isinstance(agent, MonteCarloV2Agent)
                for agent in controller.agents
            )
        )
        names = [
            player.name
            for player in controller.game.players
        ]
        self.assertEqual(len(set(names)), 4)

    def test_original_strategies_still_work(self):
        controller = create_demo_controller(
            ["Random", "Greedy", "Heuristic", "Monte Carlo"],
            mc_simulations=3,
            mc_depth=2,
        )
        self.assertIsInstance(
            controller.agents[0],
            RandomAgent,
        )
        self.assertIsInstance(
            controller.agents[1],
            GreedyAgent,
        )
        self.assertIsInstance(
            controller.agents[2],
            HeuristicAgent,
        )
        self.assertIsInstance(
            controller.agents[3],
            MonteCarloAgent,
        )

    def test_v2_supports_extended_deck(self):
        controller = create_demo_controller(
            V1_V2_DEMO_LINEUP,
            game_seed=42,
            mc_simulations=3,
            mc_depth=2,
            include_draw_four=True,
        )
        self.assertTrue(
            controller.game.include_draw_four
        )
        self.assertEqual(
            controller.game.deck.remaining_cards(),
            79,
        )
        self.assertEqual(
            len(controller.agents[1]._reference_cards),
            108,
        )

    def test_v1_v2_match_executes(self):
        controller = create_demo_controller(
            V1_V2_DEMO_LINEUP,
            game_seed=42,
            mc_simulations=3,
            mc_depth=2,
        )
        result = controller.run_game(
            max_turns=20,
            verbose=False,
        )
        self.assertGreater(
            result["total_turns"],
            0,
        )
        self.assertLessEqual(
            result["total_turns"],
            20,
        )
        self.assertEqual(
            len(result["hand_points"]),
            4,
        )


if __name__ == "__main__":
    unittest.main()

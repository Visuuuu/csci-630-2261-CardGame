import unittest
from agents.greedy_agent import GreedyAgent
from agents.heuristic_agent import HeuristicAgent
from agents.monte_carlo_agent import MonteCarloAgent
from agents.random_agent import RandomAgent
from interface.demo_config import (
    AGENT_TYPES,
    DEFAULT_LINEUP,
    create_demo_controller,
)


class TestDemoConfig(unittest.TestCase):

    def test_four_strategies_available(self):
        self.assertEqual(
            set(AGENT_TYPES),
            {
                "Random",
                "Greedy",
                "Heuristic",
                "Monte Carlo",
            },
        )

    def test_default_lineup(self):
        controller = create_demo_controller(
            DEFAULT_LINEUP
        )
        self.assertEqual(
            len(controller.game.players), 4
        )
        self.assertIsInstance(
            controller.agents[0], RandomAgent
        )
        self.assertIsInstance(
            controller.agents[1], GreedyAgent
        )
        self.assertIsInstance(
            controller.agents[2], HeuristicAgent
        )
        self.assertIsInstance(
            controller.agents[3], MonteCarloAgent
        )

    def test_duplicate_strategies_allowed(self):
        controller = create_demo_controller(
            ["Random"] * 4
        )
        self.assertTrue(
            all(
                isinstance(agent, RandomAgent)
                for agent in controller.agents
            )
        )
        names = [
            player.name
            for player in controller.game.players
        ]
        self.assertEqual(len(set(names)), 4)

    def test_mixed_strategy_assignment(self):
        controller = create_demo_controller([
            "Monte Carlo",
            "Heuristic",
            "Random",
            "Greedy",
        ])
        self.assertIsInstance(
            controller.agents[0], MonteCarloAgent
        )
        self.assertIsInstance(
            controller.agents[1], HeuristicAgent
        )
        self.assertIsInstance(
            controller.agents[2], RandomAgent
        )
        self.assertIsInstance(
            controller.agents[3], GreedyAgent
        )

    def test_reject_invalid_agent_count(self):
        with self.assertRaises(ValueError):
            create_demo_controller([
                "Random",
                "Greedy",
            ])

    def test_reject_unknown_agent(self):
        with self.assertRaises(ValueError):
            create_demo_controller([
                "Random",
                "Greedy",
                "Heuristic",
                "Unknown",
            ])

    def test_reject_invalid_monte_carlo_settings(self):
        with self.assertRaises(ValueError):
            create_demo_controller(
                DEFAULT_LINEUP,
                mc_simulations=0,
            )
        with self.assertRaises(ValueError):
            create_demo_controller(
                DEFAULT_LINEUP,
                mc_depth=0,
            )

    def test_configured_match_executes_turn(self):
        controller = create_demo_controller(
            ["Random", "Greedy", "Heuristic", "Monte Carlo"],
            game_seed=42,
            mc_simulations=5,
            mc_depth=2,
        )
        record = controller.step()
        self.assertEqual(
            controller.game.turn_count, 1
        )
        self.assertEqual(record.player_id, 0)

    def test_seeded_initial_state_is_reproducible(self):
        first = create_demo_controller(
            DEFAULT_LINEUP,
            game_seed=123,
        )
        second = create_demo_controller(
            DEFAULT_LINEUP,
            game_seed=123,
        )
        self.assertEqual(
            first.game.top_card,
            second.game.top_card,
        )
        for p1, p2 in zip(
            first.game.players,
            second.game.players,
        ):
            self.assertEqual(p1.hand, p2.hand)


if __name__ == "__main__":
    unittest.main()

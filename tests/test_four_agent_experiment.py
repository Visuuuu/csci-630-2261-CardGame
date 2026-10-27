import unittest
from collections import Counter
from agents.greedy_agent import GreedyAgent
from agents.heuristic_agent import HeuristicAgent
from agents.monte_carlo_agent import MonteCarloAgent
from agents.random_agent import RandomAgent
from experiments.compare_four_agents import (
    FourAgentConfig,
    FourAgentExperiment,
)


class TestFourAgentExperiment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A lightweight tournament for testing.
        cls.config = FourAgentConfig(
            num_games=24,
            max_turns=3,
            base_seed=42,
            mc_simulations=2,
            mc_depth=1,
        )
        cls.experiment = FourAgentExperiment(
            cls.config
        )
        cls.results = cls.experiment.run(
            verbose=False
        )

    def test_reject_invalid_game_count(self):
        with self.assertRaises(ValueError):
            FourAgentExperiment(
                FourAgentConfig(num_games=0)
            )

    def test_requires_multiple_of_24(self):
        with self.assertRaises(ValueError):
            FourAgentExperiment(
                FourAgentConfig(num_games=10)
            )

    def test_reject_invalid_parameters(self):
        with self.assertRaises(ValueError):
            FourAgentExperiment(
                FourAgentConfig(max_turns=0)
            )

        with self.assertRaises(ValueError):
            FourAgentExperiment(
                FourAgentConfig(mc_simulations=0)
            )

        with self.assertRaises(ValueError):
            FourAgentExperiment(
                FourAgentConfig(mc_depth=0)
            )

    def test_all_seating_permutations(self):
        lineups = [
            self.experiment._get_lineup(i)
            for i in range(24)
        ]
        self.assertEqual(len(set(lineups)), 24)
        for lineup in lineups:
            self.assertEqual(
                set(lineup),
                set(self.experiment.STRATEGIES),
            )

    def test_every_agent_occupies_each_seat_six_times(self):
        counts = Counter()
        for game_index in range(24):
            lineup = self.experiment._get_lineup(
                game_index
            )
            for seat, strategy in enumerate(lineup):
                counts[(strategy, seat)] += 1
        for strategy in self.experiment.STRATEGIES:
            for seat in range(4):
                self.assertEqual(
                    counts[(strategy, seat)],
                    6,
                )

    def test_correct_agent_assignment(self):
        controller = self.experiment._create_controller(0)
        agents = controller.agents
        self.assertIsInstance(agents[0], RandomAgent)
        self.assertIsInstance(agents[1], GreedyAgent)
        self.assertIsInstance(agents[2], HeuristicAgent)
        self.assertIsInstance(agents[3], MonteCarloAgent)

    def test_tournament_aggregation(self):
        results = self.results
        self.assertEqual(results["total_games"], 24)
        self.assertEqual(len(results["games"]), 24)
        self.assertEqual(
            results["completed_games"]
            + results["unfinished_games"],
            24,
        )
        total_wins = sum(
            stats["wins"]
            for stats in results["strategies"].values()
        )
        self.assertEqual(
            total_wins,
            results["completed_games"],
        )
        for stats in results["strategies"].values():
            self.assertEqual(stats["appearances"], 24)
            self.assertGreaterEqual(
                stats["average_hand_points"], 0
            )
            self.assertGreaterEqual(
                stats["win_rate_per_appearance_pct"],
                0,
            )

    def test_reproducible_game_outcomes(self):
        second_results = self.experiment.run(
            verbose=False
        )
        # Decision timing may vary, but seeded
        # game outcomes should remain the same.
        self.assertEqual(
            self.results["games"],
            second_results["games"],
        )


if __name__ == "__main__":
    unittest.main()

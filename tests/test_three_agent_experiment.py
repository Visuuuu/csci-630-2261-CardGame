import unittest
from agents.heuristic_agent import HeuristicAgent
from experiments.compare_three_agents import (
    ThreeAgentConfig,
    ThreeAgentExperiment,
)
from interface.game_controller import TurnRecord


class TestThreeAgentExperiment(unittest.TestCase):
    def setUp(self):
        self.config = ThreeAgentConfig(
            num_games=12,
            max_turns=100,
            base_seed=42,
        )
        self.experiment = ThreeAgentExperiment(
            self.config
        )

    def test_reject_invalid_game_count(self):
        with self.assertRaises(ValueError):
            ThreeAgentExperiment(
                ThreeAgentConfig(num_games=0)
            )

    def test_requires_balanced_game_count(self):
        with self.assertRaises(ValueError):
            ThreeAgentExperiment(
                ThreeAgentConfig(num_games=10)
            )

    def test_reject_invalid_turn_limit(self):
        with self.assertRaises(ValueError):
            ThreeAgentExperiment(
                ThreeAgentConfig(max_turns=0)
            )

    def test_four_players_per_game(self):
        for game_index in range(12):
            lineup = self.experiment._get_lineup(
                game_index
            )
            self.assertEqual(len(lineup), 4)
            names = [name for name, _ in lineup]
            self.assertEqual(len(set(names)), 4)

    def test_each_strategy_appears_equally(self):
        appearances = {
            "Random": 0,
            "Greedy": 0,
            "Heuristic": 0,
        }
        for game_index in range(12):
            for name, strategy in (
                self.experiment._get_lineup(game_index)
            ):
                appearances[strategy] += 1
        self.assertEqual(
            appearances,
            {
                "Random": 16,
                "Greedy": 16,
                "Heuristic": 16,
            },
        )

    def test_each_strategy_balanced_across_seats(self):
        seat_counts = {
            strategy: [0, 0, 0, 0]
            for strategy in self.experiment.STRATEGIES
        }
        for game_index in range(12):
            lineup = self.experiment._get_lineup(
                game_index
            )
            for seat, (name, strategy) in enumerate(
                lineup
            ):
                seat_counts[strategy][seat] += 1
        for counts in seat_counts.values():
            self.assertEqual(counts, [4, 4, 4, 4])

    def test_heuristic_integrates_with_controller(self):
        # Game 8 belongs to the Heuristic-duplicate group.
        controller = self.experiment._create_controller(8)
        heuristic_count = sum(
            isinstance(agent, HeuristicAgent)
            for agent in controller.agents
        )
        self.assertEqual(heuristic_count, 2)
        record = controller.step()
        self.assertIsInstance(record, TurnRecord)
        self.assertEqual(controller.game.turn_count, 1)

    def test_aggregated_results(self):
        results = self.experiment.run(verbose=False)
        self.assertEqual(results["total_games"], 12)
        self.assertEqual(
            results["completed_games"]
            + results["unfinished_games"],
            12,
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
            self.assertEqual(stats["appearances"], 16)
            self.assertGreaterEqual(
                stats["average_hand_points"], 0
            )

    def test_reproducible_game_outcomes(self):
        first = self.experiment.run(verbose=False)
        second = self.experiment.run(verbose=False)
        # Timings are hardware-dependent, but
        # seeded game outcomes should match.
        self.assertEqual(
            first["games"],
            second["games"],
        )


if __name__ == "__main__":
    unittest.main()

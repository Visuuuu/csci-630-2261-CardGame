import unittest
from experiments.compare_agents import (
    AgentExperiment,
    ExperimentConfig,
)


class TestAgentExperiment(unittest.TestCase):
    def setUp(self):
        self.config = ExperimentConfig(
            num_games=4,
            max_turns=100,
            base_seed=42,
        )
        self.experiment = AgentExperiment(self.config)

    def test_reject_invalid_game_count(self):
        with self.assertRaises(ValueError):
            AgentExperiment(
                ExperimentConfig(num_games=0)
            )

    def test_reject_invalid_turn_limit(self):
        with self.assertRaises(ValueError):
            AgentExperiment(
                ExperimentConfig(max_turns=0)
            )

    def test_rotation_covers_all_seats(self):
        positions = {
            name: set()
            for name, _ in AgentExperiment.BASE_LINEUP
        }
        for game_index in range(4):
            lineup = self.experiment._get_lineup(
                game_index
            )
            for seat, (name, strategy) in enumerate(lineup):
                positions[name].add(seat)
        for occupied_seats in positions.values():
            self.assertEqual(
                occupied_seats,
                {0, 1, 2, 3},
            )

    def test_strategy_counts_per_match(self):
        for game_index in range(4):
            lineup = self.experiment._get_lineup(
                game_index
            )
            strategies = [
                strategy
                for name, strategy in lineup
            ]
            self.assertEqual(
                strategies.count("Random"), 2
            )
            self.assertEqual(
                strategies.count("Greedy"), 2
            )

    def test_multiple_game_results(self):
        results = self.experiment.run(verbose=False)
        self.assertEqual(results["total_games"], 4)
        self.assertEqual(len(results["games"]), 4)
        self.assertEqual(
            results["completed_games"]
            + results["unfinished_games"],
            4,
        )
        for strategy in ("Random", "Greedy"):
            stats = results["strategies"][strategy]
            self.assertEqual(stats["appearances"], 8)
            self.assertGreaterEqual(
                stats["average_hand_points"], 0
            )
            self.assertGreaterEqual(
                stats["average_decision_ms"], 0
            )

    def test_wins_match_completed_games(self):
        results = self.experiment.run(verbose=False)
        total_wins = sum(
            stats["wins"]
            for stats in results["strategies"].values()
        )
        self.assertEqual(
            total_wins,
            results["completed_games"],
        )

    def test_short_turn_limit(self):
        experiment = AgentExperiment(
            ExperimentConfig(
                num_games=4,
                max_turns=1,
                base_seed=42,
            )
        )
        results = experiment.run(verbose=False)
        self.assertEqual(results["completed_games"], 0)
        self.assertEqual(results["unfinished_games"], 4)
        for stats in results["strategies"].values():
            self.assertEqual(stats["wins"], 0)

    def test_reproducible_game_outcomes(self):
        first = self.experiment.run(verbose=False)
        second = self.experiment.run(verbose=False)
        # Compare results that should be reproducible.
        # Execution timing is intentionally excluded.
        self.assertEqual(
            first["games"],
            second["games"],
        )
        self.assertEqual(
            first["completed_games"],
            second["completed_games"],
        )


if __name__ == "__main__":
    unittest.main()

import csv
import tempfile
import unittest
from pathlib import Path
from experiments.compare_four_agents import (
    FourAgentConfig,
    FourAgentExperiment,
)
from experiments.four_agent_reporting import (
    FourAgentReporter,
)


class TestFourAgentReporting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Generate a lightweight, real tournament result."""
        config = FourAgentConfig(
            num_games=24,
            max_turns=3,
            base_seed=42,
            mc_simulations=2,
            mc_depth=1,
        )
        experiment = FourAgentExperiment(config)
        cls.results = experiment.run(verbose=False)

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(
            self.temp_dir.name
        )
        self.reporter = FourAgentReporter(
            output_dir=self.output_dir
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_strategy_summary_has_four_rows(self):
        path = self.reporter.export_strategy_summary(
            self.results
        )
        self.assertTrue(path.exists())
        with path.open(
            newline="", encoding="utf-8"
        ) as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(len(rows), 4)
        self.assertEqual(
            {row["strategy"] for row in rows},
            {
                "Random",
                "Greedy",
                "Heuristic",
                "Monte Carlo",
            },
        )

    def test_game_results_have_96_rows(self):
        path = self.reporter.export_game_results(
            self.results
        )
        with path.open(
            newline="", encoding="utf-8"
        ) as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(len(rows), 96)

    def test_game_scores_are_preserved(self):
        path = self.reporter.export_game_results(
            self.results
        )
        with path.open(
            newline="", encoding="utf-8"
        ) as file:
            rows = list(csv.DictReader(file))
        first_game = self.results["games"][0]
        for row in rows[:4]:
            strategy = row["strategy"]
            self.assertEqual(
                int(row["remaining_hand_points"]),
                first_game["hand_points"][strategy],
            )
            self.assertEqual(
                int(row["seat"]),
                first_game["lineup"].index(strategy),
            )

    def test_charts_are_created(self):
        paths = self.reporter.create_charts(
            self.results
        )
        expected = {
            "win_rate.png",
            "remaining_points.png",
        }
        if self.results["completed_games"] > 0:
            expected.add("win_share.png")
        if all(
            stats["average_decision_ms"] is not None
            for stats in self.results["strategies"].values()
        ):
            expected.add("decision_time.png")
        generated = {path.name for path in paths}
        self.assertEqual(generated, expected)
        for path in paths:
            self.assertTrue(path.exists())
            self.assertGreater(
                path.stat().st_size, 0
            )

    def test_complete_report(self):
        paths = self.reporter.generate_report(
            self.results
        )
        filenames = {
            path.name for path in paths
        }
        self.assertIn(
            "strategy_summary.csv",
            filenames,
        )
        self.assertIn(
            "game_results.csv",
            filenames,
        )
        self.assertIn(
            "remaining_points.png",
            filenames,
        )
        for path in paths:
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()

import csv
import tempfile
import unittest
from pathlib import Path
from experiments.compare_agents import (
    AgentExperiment,
    ExperimentConfig,
)
from experiments.reporting import ExperimentReporter


class TestExperimentReporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run one small experiment for all tests."""
        experiment = AgentExperiment(
            ExperimentConfig(
                num_games=4,
                max_turns=100,
                base_seed=42,
            )
        )
        cls.results = experiment.run(verbose=False)

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)
        self.reporter = ExperimentReporter(
            output_dir=self.output_dir
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_strategy_csv_created(self):
        path = self.reporter.export_strategy_summary(
            self.results
        )
        self.assertTrue(path.exists())
        with path.open(
            newline="", encoding="utf-8"
        ) as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(len(rows), 2)
        strategies = {
            row["strategy"] for row in rows
        }
        self.assertEqual(
            strategies,
            {"Random", "Greedy"},
        )

    def test_game_results_csv_created(self):
        path = self.reporter.export_game_results(
            self.results
        )
        self.assertTrue(path.exists())
        with path.open(
            newline="", encoding="utf-8"
        ) as file:
            rows = list(csv.DictReader(file))
        # Four games, four players in each game.
        self.assertEqual(len(rows), 16)

    def test_exported_scores_match_results(self):
        path = self.reporter.export_game_results(
            self.results
        )
        with path.open(
            newline="", encoding="utf-8"
        ) as file:
            rows = list(csv.DictReader(file))
        first_game = self.results["games"][0]
        for row in rows[:4]:
            name = row["player_name"]
            self.assertEqual(
                int(row["remaining_hand_points"]),
                first_game["hand_points"][name],
            )

    def test_charts_created(self):
        self.reporter.create_charts(self.results)
        chart_names = [
            "remaining_points.png",
            "decision_time.png",
        ]
        if self.results["completed_games"] > 0:
            chart_names.append("win_share.png")
        for name in chart_names:
            path = self.output_dir / name
            self.assertTrue(path.exists())
            self.assertGreater(
                path.stat().st_size, 0
            )

    def test_complete_report(self):
        self.reporter.generate_report(self.results)

        self.assertTrue(
            (self.output_dir /
             "strategy_summary.csv").exists()
        )
        self.assertTrue(
            (self.output_dir /
             "game_results.csv").exists()
        )
        self.assertTrue(
            (self.output_dir /
             "remaining_points.png").exists()
        )


if __name__ == "__main__":
    unittest.main()

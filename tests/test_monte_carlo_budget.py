import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from experiments.monte_carlo_budget import (
    BudgetStudyConfig,
    STRATEGIES,
    export_csv,
    run_budget_study,
    summarize_budget,
)


def make_fake_results():
    """Produce deterministic tournament-shaped results."""
    return {
        "total_games": 24,
        "completed_games": 24,
        "unfinished_games": 0,
        "strategies": {
            strategy: {
                "wins": wins,
                "appearances": 24,
                "average_hand_points": 30.0,
                "average_decision_ms": 1.5,
                "decisions": 100,
            }
            for strategy, wins in zip(
                STRATEGIES, (3, 5, 7, 9)
            )
        },
        "games": [
            {
                "game_number": i + 1,
                "lineup": list(STRATEGIES),
                "completed": True,
                "winner": "Monte Carlo",
                "turns": 80,
                "hand_points": {
                    strategy: 10
                    for strategy in STRATEGIES
                },
            }
            for i in range(24)
        ],
    }


class TestMonteCarloBudget(unittest.TestCase):
    def test_default_configuration(self):
        config = BudgetStudyConfig()
        self.assertEqual(
            config.budgets,
            (25, 50, 100),
        )
        self.assertEqual(config.games_per_budget, 24)
        self.assertFalse(config.include_draw_four)

    def test_rejects_invalid_budgets(self):
        with self.assertRaises(ValueError):
            BudgetStudyConfig(budgets=())
        with self.assertRaises(ValueError):
            BudgetStudyConfig(budgets=(0, 25))
        with self.assertRaises(ValueError):
            BudgetStudyConfig(budgets=(25, 25))

    def test_rejects_unbalanced_game_count(self):
        with self.assertRaises(ValueError):
            BudgetStudyConfig(games_per_budget=10)
        with self.assertRaises(ValueError):
            BudgetStudyConfig(games_per_budget=0)

    def test_rejects_invalid_turns_and_depth(self):
        with self.assertRaises(ValueError):
            BudgetStudyConfig(max_turns=0)
        with self.assertRaises(ValueError):
            BudgetStudyConfig(rollout_depth=0)

    def test_summary_contains_four_strategies(self):
        rows = summarize_budget(
            25,
            make_fake_results(),
        )
        self.assertEqual(len(rows), 4)
        self.assertEqual(
            {row["strategy"] for row in rows},
            set(STRATEGIES),
        )
        mc_row = next(
            row for row in rows
            if row["strategy"] == "Monte Carlo"
        )
        self.assertEqual(mc_row["wins"], 9)
        self.assertEqual(
            mc_row["win_rate_pct"],
            37.5,
        )
        self.assertLess(
            mc_row["ci_lower_pct"],
            37.5,
        )
        self.assertGreater(
            mc_row["ci_upper_pct"],
            37.5,
        )

    @patch(
        "experiments.monte_carlo_budget."
        "FourAgentExperiment"
    )
    def test_runs_each_budget(self, mock_experiment):
        mock_experiment.return_value.run.return_value = (
            make_fake_results()
        )
        config = BudgetStudyConfig(
            budgets=(25, 50),
            games_per_budget=24,
        )
        summary, games = run_budget_study(
            config,
            verbose=False,
        )
        self.assertEqual(len(summary), 8)
        self.assertEqual(len(games), 192)
        self.assertEqual(
            mock_experiment.call_count,
            2,
        )
        configs = [
            call.args[0]
            for call in mock_experiment.call_args_list
        ]
        self.assertEqual(
            [item.mc_simulations for item in configs],
            [25, 50],
        )
        self.assertEqual(
            [item.base_seed for item in configs],
            [42, 42],
        )

    def test_csv_export(self):
        rows = summarize_budget(
            25,
            make_fake_results(),
        )
        with tempfile.TemporaryDirectory() as folder:
            path = export_csv(
                rows,
                Path(folder) / "budget.csv",
            )
            self.assertTrue(path.exists())
            with path.open(
                newline="",
                encoding="utf-8",
            ) as file:
                loaded = list(csv.DictReader(file))
            self.assertEqual(len(loaded), 4)
            self.assertEqual(
                loaded[0]["mc_simulations"],
                "25",
            )


if __name__ == "__main__":
    unittest.main()

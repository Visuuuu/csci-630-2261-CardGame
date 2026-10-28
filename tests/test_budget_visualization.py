import csv
import tempfile
import unittest
from pathlib import Path
from experiments.plot_monte_carlo_budget import (
    MonteCarloBudgetPlotter,
    load_monte_carlo_results,
)


class TestBudgetVisualization(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.csv_path = (
            self.directory / "budget_summary.csv"
        )
        self.rows = [
            {
                "mc_simulations": budget,
                "strategy": "Monte Carlo",
                "wins": wins,
                "appearances": 24,
                "win_rate_pct": 100 * wins / 24,
                "ci_lower_pct": lower,
                "ci_upper_pct": upper,
                "average_hand_points": points,
                "average_decision_ms": time,
            }
            for budget, wins, lower, upper, points, time in [
                (25, 5, 9.0, 40.0, 35.0, 3.5),
                (50, 7, 14.0, 49.0, 30.0, 7.0),
                (100, 6, 12.0, 45.0, 32.0, 14.0),
            ]
        ]
        self._write_csv(self.rows)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_csv(self, rows):
        with self.csv_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(self.rows[0].keys()),
            )
            writer.writeheader()
            writer.writerows(rows)

    def test_loads_three_monte_carlo_budgets(self):
        loaded = load_monte_carlo_results(
            self.csv_path
        )
        self.assertEqual(len(loaded), 3)
        self.assertEqual(
            [row["budget"] for row in loaded],
            [25, 50, 100],
        )

    def test_sorts_budgets_numerically(self):
        self._write_csv(
            list(reversed(self.rows))
        )
        loaded = load_monte_carlo_results(
            self.csv_path
        )
        self.assertEqual(
            [row["budget"] for row in loaded],
            [25, 50, 100],
        )

    def test_ignores_other_strategies(self):
        extra = {
            **self.rows[0],
            "strategy": "Random",
        }
        self._write_csv(
            self.rows + [extra]
        )
        loaded = load_monte_carlo_results(
            self.csv_path
        )
        self.assertEqual(len(loaded), 3)

    def test_missing_file_raises_error(self):
        missing = self.directory / "missing.csv"
        with self.assertRaises(FileNotFoundError):
            load_monte_carlo_results(missing)

    def test_duplicate_budget_rejected(self):
        self._write_csv(
            self.rows + [self.rows[0]]
        )
        with self.assertRaises(ValueError):
            load_monte_carlo_results(
                self.csv_path
            )

    def test_invalid_numeric_value_rejected(self):
        invalid_rows = [
            dict(row) for row in self.rows
        ]
        invalid_rows[0]["average_decision_ms"] = (
            "invalid"
        )
        self._write_csv(invalid_rows)
        with self.assertRaises(ValueError):
            load_monte_carlo_results(
                self.csv_path
            )

    def test_four_charts_are_created(self):
        loaded = load_monte_carlo_results(
            self.csv_path
        )
        plotter = MonteCarloBudgetPlotter(
            self.directory / "charts"
        )
        paths = plotter.generate_all(loaded)
        self.assertEqual(len(paths), 4)
        expected_names = {
            "budget_win_rate.png",
            "budget_remaining_points.png",
            "budget_decision_time.png",
            "budget_tradeoff.png",
        }
        self.assertEqual(
            {path.name for path in paths},
            expected_names,
        )
        for path in paths:
            with self.subTest(path=path.name):
                self.assertTrue(path.exists())
                self.assertGreater(
                    path.stat().st_size,
                    0,
                )
                with path.open("rb") as file:
                    self.assertEqual(
                        file.read(8),
                        b"\x89PNG\r\n\x1a\n",
                    )


if __name__ == "__main__":
    unittest.main()

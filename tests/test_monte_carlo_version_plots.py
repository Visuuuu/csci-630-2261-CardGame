import csv
import tempfile
import unittest
from pathlib import Path
from experiments.plot_monte_carlo_versions import (
    MonteCarloVersionPlotter,
    load_version_summary,
    load_paired_games,
    summarize_paired_outcomes,
)


class TestMonteCarloVersionPlots(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp_dir.name)
        self.summary_path = (
            self.folder / "version_summary.csv"
        )
        self.paired_path = (
            self.folder / "paired_games.csv"
        )
        self.summary_rows = [
            {
                "version": "V1",
                "strategy": "Monte Carlo",
                "wins": 5,
                "appearances": 24,
                "win_rate_pct": 100 * 5 / 24,
                "ci_lower_pct": 9.0,
                "ci_upper_pct": 40.0,
                "average_hand_points": 34.0,
                "average_decision_ms": 4.2,
            },
            {
                "version": "V2",
                "strategy": "Monte Carlo",
                "wins": 8,
                "appearances": 24,
                "win_rate_pct": 100 * 8 / 24,
                "ci_lower_pct": 18.0,
                "ci_upper_pct": 54.0,
                "average_hand_points": 28.0,
                "average_decision_ms": 8.9,
            },
        ]

        self.paired_rows = [
            self.make_pair(1, 1, 1),
            self.make_pair(2, 1, 0),
            self.make_pair(3, 0, 1),
            self.make_pair(4, 0, 1),
            self.make_pair(5, 0, 0),
        ]

        self.write_csv(
            self.summary_path,
            self.summary_rows,
        )
        self.write_csv(
            self.paired_path,
            self.paired_rows,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    @staticmethod
    def make_pair(number, v1_won, v2_won):
        return {
            "game_number": number,
            "mc_seat": (number - 1) % 4,
            "v1_mc_won": v1_won,
            "v2_mc_won": v2_won,
            "v1_mc_points": 30,
            "v2_mc_points": 20,
            "points_change_v2_minus_v1": -10,
        }

    @staticmethod
    def write_csv(path, rows):
        with path.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(rows[0]),
            )
            writer.writeheader()
            writer.writerows(rows)

    def test_loads_both_versions(self):
        rows = load_version_summary(
            self.summary_path
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(
            [row["version"] for row in rows],
            ["V1", "V2"],
        )

    def test_summary_filters_other_agents(self):
        extra = {
            **self.summary_rows[0],
            "strategy": "Random",
        }
        self.write_csv(
            self.summary_path,
            self.summary_rows + [extra],
        )
        rows = load_version_summary(
            self.summary_path
        )
        self.assertEqual(len(rows), 2)

    def test_duplicate_version_rejected(self):
        self.write_csv(
            self.summary_path,
            self.summary_rows + [self.summary_rows[0]],
        )
        with self.assertRaises(ValueError):
            load_version_summary(
                self.summary_path
            )

    def test_invalid_win_rate_rejected(self):
        rows = [
            dict(row) for row in self.summary_rows
        ]
        rows[0]["win_rate_pct"] = 90.0
        self.write_csv(self.summary_path, rows)
        with self.assertRaises(ValueError):
            load_version_summary(
                self.summary_path
            )

    def test_loads_paired_games(self):
        rows = load_paired_games(
            self.paired_path
        )
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["game_number"], 1)

    def test_outcome_categories(self):
        rows = load_paired_games(
            self.paired_path
        )
        counts = summarize_paired_outcomes(rows)
        self.assertEqual(
            counts,
            {
                "Both win": 1,
                "V1 only": 1,
                "V2 only": 2,
                "Neither": 1,
            },
        )

    def test_inconsistent_points_rejected(self):
        rows = [
            dict(row) for row in self.paired_rows
        ]
        rows[0]["points_change_v2_minus_v1"] = 5
        self.write_csv(self.paired_path, rows)
        with self.assertRaises(ValueError):
            load_paired_games(self.paired_path)

    def test_generates_four_png_charts(self):
        summary = load_version_summary(
            self.summary_path
        )
        paired = load_paired_games(
            self.paired_path
        )
        plotter = MonteCarloVersionPlotter(
            self.folder / "charts"
        )
        paths = plotter.generate_all(
            summary, paired
        )
        self.assertEqual(len(paths), 4)
        expected = {
            "version_win_rate.png",
            "version_remaining_points.png",
            "version_decision_time.png",
            "version_paired_outcomes.png",
        }
        self.assertEqual(
            {path.name for path in paths},
            expected,
        )
        for path in paths:
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())
                self.assertGreater(
                    path.stat().st_size, 0
                )
                with path.open("rb") as file:
                    self.assertEqual(
                        file.read(8),
                        b"\x89PNG\r\n\x1a\n",
                    )


if __name__ == "__main__":
    unittest.main()

import csv
import json
import tempfile
import unittest
from pathlib import Path
from experiments.final_analysis import (
    analyze_results,
    build_markdown_report,
    count,
    export_final_analysis,
    numeric,
    paired_outcomes,
    read_csv,
    validate_strategy_rows,
)


STRATEGIES = (
    "Random",
    "Greedy",
    "Heuristic",
    "Monte Carlo",
)


def make_group(group_field, group_value, mc_wins=6):
    """Create one complete synthetic strategy group."""
    wins = {
        "Random": 4,
        "Greedy": 6,
        "Heuristic": 14 - mc_wins,
        "Monte Carlo": mc_wins,
    }
    return [
        {
            group_field: str(group_value),
            "strategy": strategy,
            "wins": wins[strategy],
            "appearances": 24,
            "win_rate_pct": (
                100 * wins[strategy] / 24
            ),
            "ci_lower_pct": 0.0,
            "ci_upper_pct": 100.0,
            "average_hand_points": 30.0,
            "average_decision_ms": 2.5,
        }
        for strategy in STRATEGIES
    ]


def make_inputs():
    validation = (
        make_group("ruleset", "baseline_104")
        + make_group("ruleset", "extended_108")
    )
    budgets = []
    for budget in (25, 50, 100):
        budgets.extend(
            make_group(
                "mc_simulations",
                budget,
                mc_wins={25: 5, 50: 7, 100: 6}[budget],
            )
        )
    versions = (
        make_group("version", "V1", mc_wins=5)
        + make_group("version", "V2", mc_wins=8)
    )
    paired = []
    for game_number in range(1, 25):
        v1_won = int(game_number <= 5)
        v2_won = int(game_number <= 8)
        paired.append({
            "game_number": game_number,
            "v1_mc_won": v1_won,
            "v2_mc_won": v2_won,
            "v1_mc_points": 30,
            "v2_mc_points": 20,
            "points_change_v2_minus_v1": -10,
        })
    return validation, budgets, versions, paired


class TestFinalAnalysis(unittest.TestCase):
    def test_numeric_validation(self):
        row = {"value": "12.5"}
        self.assertEqual(
            numeric(row, "value"),
            12.5,
        )
        with self.assertRaises(ValueError):
            numeric({"value": "NaN"}, "value")

    def test_integer_count_validation(self):
        self.assertEqual(
            count({"wins": "6"}, "wins"),
            6,
        )
        with self.assertRaises(ValueError):
            count({"wins": "2.5"}, "wins")

    def test_rejects_missing_strategy(self):
        rows = make_group(
            "ruleset",
            "baseline_104",
        )
        with self.assertRaises(ValueError):
            validate_strategy_rows(
                rows[:-1],
                "ruleset",
            )

    def test_rejects_incorrect_win_rate(self):
        rows = make_group(
            "ruleset",
            "baseline_104",
        )
        rows[0]["win_rate_pct"] = 99.0
        with self.assertRaises(ValueError):
            validate_strategy_rows(
                rows,
                "ruleset",
            )

    def test_paired_outcome_counts(self):
        _, _, _, paired = make_inputs()
        outcomes = paired_outcomes(paired)
        self.assertEqual(
            outcomes["both_win"],
            5,
        )
        self.assertEqual(
            outcomes["v2_only"],
            3,
        )
        self.assertEqual(
            outcomes["v1_only"],
            0,
        )
        self.assertEqual(
            outcomes["neither_wins"],
            16,
        )
        self.assertEqual(
            outcomes["total_pairs"],
            24,
        )

    def test_final_comparison_calculations(self):
        analysis = analyze_results(
            *make_inputs()
        )
        comparison = analysis["comparison"]
        self.assertAlmostEqual(
            comparison["v1_win_rate_pct"],
            100 * 5 / 24,
        )
        self.assertAlmostEqual(
            comparison["v2_win_rate_pct"],
            100 * 8 / 24,
        )
        self.assertAlmostEqual(
            comparison["win_rate_change_pp"],
            12.5,
        )
        self.assertEqual(
            comparison[
                "highest_observed_win_rate_budget"
            ],
            50,
        )

    def test_markdown_and_json_export(self):
        analysis = analyze_results(
            *make_inputs()
        )
        with tempfile.TemporaryDirectory() as folder:
            markdown_path, json_path = (
                export_final_analysis(
                    analysis,
                    Path(folder) / "final",
                )
            )
            self.assertTrue(markdown_path.is_file())
            self.assertTrue(json_path.is_file())
            markdown = markdown_path.read_text(
                encoding="utf-8"
            )
            self.assertIn(
                "Monte Carlo V1 versus V2",
                markdown,
            )
            self.assertIn(
                "baseline_104",
                markdown,
            )
            with json_path.open(
                encoding="utf-8"
            ) as file:
                saved = json.load(file)
            self.assertAlmostEqual(
                saved["comparison"][
                    "win_rate_change_pp"
                ],
                12.5,
            )

    def test_read_csv_and_missing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data.csv"
            with path.open(
                "w",
                newline="",
                encoding="utf-8",
            ) as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=["strategy", "wins"],
                )
                writer.writeheader()
                writer.writerow({
                    "strategy": "Random",
                    "wins": 3,
                })
            rows = read_csv(path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["wins"], "3")
            with self.assertRaises(FileNotFoundError):
                read_csv(
                    Path(folder) / "missing.csv"
                )


if __name__ == "__main__":
    unittest.main()

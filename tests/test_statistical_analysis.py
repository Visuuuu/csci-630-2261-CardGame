import csv
import tempfile
import unittest
from pathlib import Path
from experiments.compare_four_agents import (
    FourAgentConfig,
    FourAgentExperiment,
)
from experiments.statistical_analysis import (
    wilson_confidence_interval,
    analyze_tournament,
    export_statistical_summary,
)


class TestStatisticalAnalysis(unittest.TestCase):
    def setUp(self):
        # Small synthetic results let us test the
        # calculations without running tournaments.
        self.results = {
            "total_games": 24,
            "completed_games": 22,
            "unfinished_games": 2,
            "strategies": {
                "Random": {
                    "wins": 3,
                    "appearances": 24,
                    "average_hand_points": 45.0,
                    "average_decision_ms": 0.01,
                    "decisions": 100,
                },
                "Greedy": {
                    "wins": 5,
                    "appearances": 24,
                    "average_hand_points": 35.0,
                    "average_decision_ms": 0.02,
                    "decisions": 100,
                },
                "Heuristic": {
                    "wins": 8,
                    "appearances": 24,
                    "average_hand_points": 25.0,
                    "average_decision_ms": 0.03,
                    "decisions": 100,
                },
                "Monte Carlo": {
                    "wins": 6,
                    "appearances": 24,
                    "average_hand_points": 30.0,
                    "average_decision_ms": 5.0,
                    "decisions": 100,
                },
            },
        }

    def test_wilson_interval_contains_estimate(self):
        lower, upper = wilson_confidence_interval(
            wins=6,
            games=24,
        )
        self.assertLess(lower, 25.0)
        self.assertGreater(upper, 25.0)

    def test_zero_wins_has_valid_interval(self):
        lower, upper = wilson_confidence_interval(
            wins=0,
            games=24,
        )

        self.assertAlmostEqual(lower, 0.0, places=10)
        self.assertGreater(upper, 0.0)
        self.assertLessEqual(upper, 100.0)

    def test_all_wins_has_valid_interval(self):
        lower, upper = wilson_confidence_interval(
            wins=24,
            games=24,
        )
        self.assertGreaterEqual(lower, 0.0)
        self.assertLess(lower, 100.0)
        self.assertAlmostEqual(upper, 100.0)

    def test_invalid_interval_inputs(self):
        with self.assertRaises(ValueError):
            wilson_confidence_interval(0, 0)
        with self.assertRaises(ValueError):
            wilson_confidence_interval(-1, 24)
        with self.assertRaises(ValueError):
            wilson_confidence_interval(25, 24)

    def test_analysis_has_four_strategies(self):
        rows = analyze_tournament(
            self.results,
            ruleset="baseline_104",
            mc_simulations=25,
            mc_depth=3,
        )
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

    def test_win_rate_uses_all_appearances(self):
        rows = analyze_tournament(
            self.results,
            ruleset="baseline_104",
            mc_simulations=25,
            mc_depth=3,
        )
        random_row = next(
            row for row in rows
            if row["strategy"] == "Random"
        )
        # 3 wins / 24 appearances, not 22 finishes.
        self.assertAlmostEqual(
            random_row["win_rate_pct"],
            12.5,
        )
        self.assertEqual(
            random_row["unfinished_games"], 2
        )

    def test_csv_export(self):
        rows = analyze_tournament(
            self.results,
            ruleset="extended_108",
            mc_simulations=50,
            mc_depth=3,
        )
        with tempfile.TemporaryDirectory() as temp:
            path = export_statistical_summary(
                rows,
                Path(temp) / "stats.csv",
            )
            self.assertTrue(path.exists())
            with path.open(
                newline="",
                encoding="utf-8",
            ) as file:
                loaded = list(csv.DictReader(file))
            self.assertEqual(len(loaded), 4)
            self.assertEqual(
                loaded[0]["ruleset"],
                "extended_108",
            )
            self.assertEqual(
                loaded[0]["mc_simulations"],
                "50",
            )

    def test_both_tournament_rulesets(self):
        baseline = FourAgentExperiment(
            FourAgentConfig(
                include_draw_four=False,
            )
        )
        extended = FourAgentExperiment(
            FourAgentConfig(
                include_draw_four=True,
            )
        )
        baseline_controller = (
            baseline._create_controller(0)
        )
        extended_controller = (
            extended._create_controller(0)
        )
        self.assertEqual(
            baseline_controller.game.deck.remaining_cards(),
            75,
        )
        self.assertEqual(
            extended_controller.game.deck.remaining_cards(),
            79,
        )
        self.assertFalse(
            baseline_controller.game.include_draw_four
        )
        self.assertTrue(
            extended_controller.game.include_draw_four
        )


if __name__ == "__main__":
    unittest.main()

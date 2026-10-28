import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from agents.monte_carlo_agent import MonteCarloAgent
from agents.monte_carlo_v2_agent import MonteCarloV2Agent
from experiments.compare_four_agents import (
    FourAgentConfig,
    FourAgentExperiment,
)
from experiments.compare_monte_carlo_versions import (
    MonteCarloV2Experiment,
    VersionComparisonConfig,
    create_paired_game_rows,
    export_csv,
    run_version_comparison,
    summarize_version,
)


STRATEGIES = (
    "Random", "Greedy", "Heuristic", "Monte Carlo"
)


def fake_results(mc_wins=5):
    """Create a small, consistent tournament-shaped result."""
    wins = {
        "Random": 4,
        "Greedy": 6,
        "Heuristic": 14 - mc_wins,
        "Monte Carlo": mc_wins,
    }
    return {
        "total_games": 24,
        "completed_games": 24,
        "unfinished_games": 0,
        "strategies": {
            name: {
                "wins": wins[name],
                "appearances": 24,
                "average_hand_points": 30.0,
                "average_decision_ms": 2.0,
                "decisions": 100,
            }
            for name in STRATEGIES
        },
        "games": [
            {
                "game_number": i + 1,
                "lineup": list(STRATEGIES),
                "completed": True,
                "winner": (
                    "Monte Carlo" if i < mc_wins
                    else "Heuristic"
                ),
                "turns": 75,
                "hand_points": {
                    name: (
                        20 if name == "Monte Carlo"
                        else 30
                    )
                    for name in STRATEGIES
                },
            }
            for i in range(24)
        ],
    }


class TestMonteCarloVersions(unittest.TestCase):
    def test_default_configuration(self):
        config = VersionComparisonConfig()

        self.assertEqual(config.num_games, 24)
        self.assertEqual(config.mc_simulations, 25)
        self.assertFalse(config.include_draw_four)

    def test_rejects_invalid_configuration(self):
        with self.assertRaises(ValueError):
            VersionComparisonConfig(num_games=10)
        with self.assertRaises(ValueError):
            VersionComparisonConfig(max_turns=0)
        with self.assertRaises(ValueError):
            VersionComparisonConfig(mc_simulations=0)
        with self.assertRaises(ValueError):
            VersionComparisonConfig(mc_depth=0)

    def test_v2_replaces_only_monte_carlo(self):
        config = FourAgentConfig(
            num_games=24,
            mc_simulations=5,
            mc_depth=2,
        )
        original = FourAgentExperiment(config)
        improved = MonteCarloV2Experiment(config)
        # Check every seat permutation.
        for game_index in range(24):
            v1 = original._create_controller(game_index)
            v2 = improved._create_controller(game_index)
            lineup = original._get_lineup(game_index)
            mc_seat = lineup.index("Monte Carlo")
            self.assertIsInstance(
                v1.agents[mc_seat],
                MonteCarloAgent,
            )
            self.assertNotIsInstance(
                v1.agents[mc_seat],
                MonteCarloV2Agent,
            )
            self.assertIsInstance(
                v2.agents[mc_seat],
                MonteCarloV2Agent,
            )
            # Initial decks and hands must match.
            self.assertEqual(
                v1.game.top_card,
                v2.game.top_card,
            )
            for p1, p2 in zip(
                v1.game.players,
                v2.game.players,
            ):
                self.assertEqual(p1.hand, p2.hand)

    def test_version_summary_has_valid_interval(self):
        rows = summarize_version(
            "V1",
            fake_results(mc_wins=5),
        )
        self.assertEqual(len(rows), 4)
        mc_row = next(
            row for row in rows
            if row["strategy"] == "Monte Carlo"
        )
        self.assertEqual(mc_row["wins"], 5)
        self.assertEqual(mc_row["version"], "V1")
        self.assertLess(
            mc_row["ci_lower_pct"],
            mc_row["win_rate_pct"],
        )
        self.assertGreater(
            mc_row["ci_upper_pct"],
            mc_row["win_rate_pct"],
        )

    def test_paired_game_rows(self):
        v1 = fake_results(mc_wins=5)
        v2 = fake_results(mc_wins=8)
        for game in v2["games"]:
            game["hand_points"]["Monte Carlo"] = 15
        paired = create_paired_game_rows(
            v1, v2
        )
        self.assertEqual(len(paired), 24)
        self.assertEqual(
            paired[0]["points_change_v2_minus_v1"],
            -5,
        )
        self.assertEqual(
            sum(row["v1_mc_won"] for row in paired),
            5,
        )
        self.assertEqual(
            sum(row["v2_mc_won"] for row in paired),
            8,
        )

    def test_rejects_mismatched_games(self):
        v1 = fake_results()
        v2 = fake_results()
        v2["games"][0]["lineup"] = list(
            reversed(STRATEGIES)
        )
        with self.assertRaises(ValueError):
            create_paired_game_rows(v1, v2)

    @patch(
        "experiments.compare_four_agents."
        "FourAgentExperiment.run"
    )
    def test_runs_both_versions(self, mock_run):
        mock_run.side_effect = [
            fake_results(mc_wins=5),
            fake_results(mc_wins=8),
        ]
        summary, paired = run_version_comparison(
            VersionComparisonConfig(),
            verbose=False,
        )
        self.assertEqual(mock_run.call_count, 2)
        self.assertEqual(len(summary), 8)
        self.assertEqual(len(paired), 24)
        versions = {
            row["version"] for row in summary
        }
        self.assertEqual(versions, {"V1", "V2"})

    def test_csv_export(self):
        rows = summarize_version(
            "V2",
            fake_results(mc_wins=8),
        )
        with tempfile.TemporaryDirectory() as folder:
            path = export_csv(
                rows,
                Path(folder) / "comparison.csv",
            )
            with path.open(
                newline="",
                encoding="utf-8",
            ) as file:
                loaded = list(csv.DictReader(file))
            self.assertEqual(len(loaded), 4)
            self.assertEqual(
                loaded[0]["version"],
                "V2",
            )


if __name__ == "__main__":
    unittest.main()

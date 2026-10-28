import csv
from dataclasses import dataclass
from pathlib import Path
from agents.monte_carlo_v2_agent import MonteCarloV2Agent
from experiments.compare_four_agents import (
    FourAgentConfig,
    FourAgentExperiment,
)
from experiments.statistical_analysis import (
    wilson_confidence_interval,
)


@dataclass(frozen=True)
class VersionComparisonConfig:
    """Shared settings for both Monte Carlo versions."""
    num_games: int = 24
    max_turns: int = 1000
    base_seed: int = 42
    mc_simulations: int = 25
    mc_depth: int = 3
    include_draw_four: bool = False
    def __post_init__(self):
        if self.num_games <= 0 or self.num_games % 24:
            raise ValueError(
                "num_games must be a positive multiple of 24."
            )
        if self.max_turns <= 0:
            raise ValueError("max_turns must be positive.")
        if self.mc_simulations <= 0:
            raise ValueError(
                "mc_simulations must be positive."
            )
        if self.mc_depth <= 0:
            raise ValueError("mc_depth must be positive.")


class MonteCarloV2Experiment(FourAgentExperiment):
    """Run the usual four-agent tournament using V2."""
    def _create_controller(self, game_index: int):
        # First create the ordinary tournament game.
        controller = super()._create_controller(
            game_index
        )
        # Replace only Monte Carlo V1 with V2.
        lineup = self._get_lineup(game_index)
        monte_carlo_seat = lineup.index("Monte Carlo")
        # Match the V1 seed formula exactly.
        monte_carlo_seed = (
            self.config.base_seed * 100_000
            + game_index * 10
            + 4
        )
        controller.agents[monte_carlo_seat] = (
            MonteCarloV2Agent(
                num_simulations=self.config.mc_simulations,
                rollout_depth=self.config.mc_depth,
                seed=monte_carlo_seed,
                include_draw_four=(
                    self.config.include_draw_four
                ),
            )
        )
        return controller


def summarize_version(
    version: str,
    results: dict,
) -> list[dict]:
    """Summarize all four strategies for one version."""
    rows = []
    for strategy, stats in results["strategies"].items():
        wins = stats["wins"]
        appearances = stats["appearances"]
        lower, upper = wilson_confidence_interval(
            wins,
            appearances,
        )
        rows.append({
            "version": version,
            "strategy": strategy,
            "total_games": results["total_games"],
            "completed_games": results["completed_games"],
            "unfinished_games": results["unfinished_games"],
            "wins": wins,
            "appearances": appearances,
            "win_rate_pct": 100 * wins / appearances,
            "ci_lower_pct": lower,
            "ci_upper_pct": upper,
            "average_hand_points": stats[
                "average_hand_points"
            ],
            "average_decision_ms": stats[
                "average_decision_ms"
            ],
            "total_decisions": stats["decisions"],
        })
    return rows


def create_paired_game_rows(
    v1_results: dict,
    v2_results: dict,
) -> list[dict]:
    """Compare outcomes sharing seed and seat assignment."""
    v1_games = v1_results["games"]
    v2_games = v2_results["games"]
    if len(v1_games) != len(v2_games):
        raise ValueError(
            "Both versions must have the same game count."
        )
    rows = []
    for v1, v2 in zip(v1_games, v2_games):
        if (
            v1["game_number"] != v2["game_number"]
            or v1["lineup"] != v2["lineup"]
        ):
            raise ValueError(
                "Game numbers and lineups must match."
            )
        v1_points = v1["hand_points"]["Monte Carlo"]
        v2_points = v2["hand_points"]["Monte Carlo"]
        rows.append({
            "game_number": v1["game_number"],
            "mc_seat": v1["lineup"].index("Monte Carlo"),
            "v1_completed": v1["completed"],
            "v2_completed": v2["completed"],
            "v1_winner": v1["winner"] or "",
            "v2_winner": v2["winner"] or "",
            "v1_mc_won": int(
                v1["completed"]
                and v1["winner"] == "Monte Carlo"
            ),
            "v2_mc_won": int(
                v2["completed"]
                and v2["winner"] == "Monte Carlo"
            ),
            "v1_mc_points": v1_points,
            "v2_mc_points": v2_points,
            "points_change_v2_minus_v1": (
                v2_points - v1_points
            ),
            "v1_turns": v1["turns"],
            "v2_turns": v2["turns"],
        })
    return rows


def run_version_comparison(
    config: VersionComparisonConfig,
    verbose: bool = True,
) -> tuple[list[dict], list[dict]]:
    """Run matched V1 and V2 tournament configurations."""
    tournament_config = FourAgentConfig(
        num_games=config.num_games,
        max_turns=config.max_turns,
        base_seed=config.base_seed,
        mc_simulations=config.mc_simulations,
        mc_depth=config.mc_depth,
        include_draw_four=config.include_draw_four,
    )
    if verbose:
        print("\nRunning Monte Carlo V1 tournament...")
    v1_experiment = FourAgentExperiment(
        tournament_config
    )
    v1_results = v1_experiment.run(verbose=verbose)
    if verbose:
        print("\nRunning Monte Carlo V2 tournament...")
    v2_experiment = MonteCarloV2Experiment(
        tournament_config
    )
    v2_results = v2_experiment.run(verbose=verbose)
    summary_rows = (
        summarize_version("V1", v1_results)
        + summarize_version("V2", v2_results)
    )
    paired_rows = create_paired_game_rows(
        v1_results,
        v2_results,
    )
    return summary_rows, paired_rows


def export_csv(
    rows: list[dict],
    output_path: str | Path,
) -> Path:
    """Export comparison results to CSV."""
    if not rows:
        raise ValueError("Cannot export empty results.")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0]),
        )
        writer.writeheader()
        writer.writerows(rows)
    return path


def print_comparison(summary_rows: list[dict]):
    """Print Monte Carlo V1 and V2 results."""
    print("\n" + "=" * 72)
    print("MONTE CARLO V1 VS V2")
    print("=" * 72)
    for row in summary_rows:
        if row["strategy"] != "Monte Carlo":
            continue
        decision_time = row["average_decision_ms"]
        time_text = (
            f"{decision_time:.5f} ms"
            if decision_time is not None
            else "N/A"
        )
        print(f"\n{row['version']}")
        print(f"  Wins: {row['wins']}")
        print(f"  Win rate: {row['win_rate_pct']:.2f}%")
        print(
            "  95% Wilson interval: "
            f"[{row['ci_lower_pct']:.2f}%, "
            f"{row['ci_upper_pct']:.2f}%]"
        )
        print(
            "  Average remaining points: "
            f"{row['average_hand_points']:.2f}"
        )
        print(f"  Average decision time: {time_text}")
        print(
            "  Unfinished games: "
            f"{row['unfinished_games']}"
        )
    print("=" * 72)


def main():
    config = VersionComparisonConfig(
        num_games=24,
        max_turns=1000,
        base_seed=42,
        mc_simulations=25,
        mc_depth=3,
        include_draw_four=False,
    )
    summary_rows, paired_rows = (
        run_version_comparison(config)
    )
    output_dir = Path(
        "reports/monte_carlo_versions"
    )
    summary_path = export_csv(
        summary_rows,
        output_dir / "version_summary.csv",
    )
    paired_path = export_csv(
        paired_rows,
        output_dir / "paired_games.csv",
    )
    print_comparison(summary_rows)
    print("\nGenerated reports:")
    print(summary_path.resolve())
    print(paired_path.resolve())


if __name__ == "__main__":
    main()

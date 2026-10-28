import csv
from dataclasses import dataclass
from pathlib import Path
from experiments.compare_four_agents import (
    FourAgentConfig,
    FourAgentExperiment,
)
from experiments.statistical_analysis import (
    wilson_confidence_interval,
)


STRATEGIES = (
    "Random",
    "Greedy",
    "Heuristic",
    "Monte Carlo",
)


@dataclass(frozen=True)
class BudgetStudyConfig:
    """Configuration for the Monte Carlo budget study."""
    budgets: tuple[int, ...] = (25, 50, 100)
    games_per_budget: int = 24
    max_turns: int = 1000
    base_seed: int = 42
    rollout_depth: int = 3
    include_draw_four: bool = False
    def __post_init__(self):
        if not self.budgets:
            raise ValueError("At least one budget is required.")
        if any(budget <= 0 for budget in self.budgets):
            raise ValueError("Budgets must be positive.")
        if len(set(self.budgets)) != len(self.budgets):
            raise ValueError("Budgets must be unique.")
        if (
            self.games_per_budget <= 0
            or self.games_per_budget % 24 != 0
        ):
            raise ValueError(
                "games_per_budget must be a positive "
                "multiple of 24."
            )
        if self.max_turns <= 0:
            raise ValueError("max_turns must be positive.")
        if self.rollout_depth <= 0:
            raise ValueError(
                "rollout_depth must be positive."
            )


def summarize_budget(
    budget: int,
    results: dict,
) -> list[dict]:
    """Create summary rows for all four strategies."""
    rows = []
    for strategy in STRATEGIES:
        stats = results["strategies"][strategy]
        wins = stats["wins"]
        appearances = stats["appearances"]
        lower, upper = wilson_confidence_interval(
            wins,
            appearances,
        )
        rows.append({
            "mc_simulations": budget,
            "strategy": strategy,
            "total_games": results["total_games"],
            "completed_games": results["completed_games"],
            "unfinished_games": results["unfinished_games"],
            "wins": wins,
            "appearances": appearances,
            "win_rate_pct": (
                100.0 * wins / appearances
            ),
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


def run_budget_study(
    config: BudgetStudyConfig,
    verbose: bool = True,
) -> tuple[list[dict], list[dict]]:
    """Run one four-agent tournament for each budget.
    Returns:
        summary_rows: Strategy-level results.
        game_rows: Individual game/strategy results.
    """
    summary_rows = []
    game_rows = []
    for budget in config.budgets:
        if verbose:
            print("\n" + "=" * 60)
            print(
                f"Monte Carlo budget: "
                f"{budget} simulations per candidate"
            )
            print("=" * 60)
        tournament_config = FourAgentConfig(
            num_games=config.games_per_budget,
            max_turns=config.max_turns,
            base_seed=config.base_seed,
            mc_simulations=budget,
            mc_depth=config.rollout_depth,
            include_draw_four=config.include_draw_four,
        )
        experiment = FourAgentExperiment(
            tournament_config
        )
        results = experiment.run(verbose=verbose)
        summary_rows.extend(
            summarize_budget(budget, results)
        )
        for game in results["games"]:
            for seat, strategy in enumerate(
                game["lineup"]
            ):
                game_rows.append({
                    "mc_simulations": budget,
                    "game_number": game["game_number"],
                    "seed": (
                        config.base_seed
                        + game["game_number"] - 1
                    ),
                    "seat": seat,
                    "strategy": strategy,
                    "completed": game["completed"],
                    "winner": game["winner"] or "",
                    "won": int(
                        game["completed"]
                        and game["winner"] == strategy
                    ),
                    "turns": game["turns"],
                    "remaining_hand_points": (
                        game["hand_points"][strategy]
                    ),
                })
    return summary_rows, game_rows


def export_csv(
    rows: list[dict],
    path: str | Path,
) -> Path:
    """Export experiment rows to a CSV file."""
    if not rows:
        raise ValueError("Cannot export empty results.")
    path = Path(path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)
    return path


def print_budget_comparison(
    summary_rows: list[dict],
) -> None:
    """Print Monte Carlo results for each budget."""
    print("\n" + "=" * 78)
    print("MONTE CARLO SIMULATION BUDGET COMPARISON")
    print("=" * 78)
    header = (
        f"{'Budget':>8}"
        f"{'Wins':>8}"
        f"{'Win Rate':>12}"
        f"{'Avg Points':>14}"
        f"{'Avg Time (ms)':>18}"
    )
    print(header)
    print("-" * 78)
    for row in summary_rows:
        if row["strategy"] != "Monte Carlo":
            continue
        time_ms = row["average_decision_ms"]
        time_text = (
            f"{time_ms:.5f}"
            if time_ms is not None
            else "N/A"
        )
        print(
            f"{row['mc_simulations']:>8}"
            f"{row['wins']:>8}"
            f"{row['win_rate_pct']:>11.2f}%"
            f"{row['average_hand_points']:>14.2f}"
            f"{time_text:>18}"
        )
    print("=" * 78)


def main():
    config = BudgetStudyConfig(
        budgets=(25, 50, 100),
        games_per_budget=24,
        max_turns=1000,
        base_seed=42,
        rollout_depth=3,
        include_draw_four=False,
    )
    summary_rows, game_rows = run_budget_study(
        config,
        verbose=True,
    )
    output_dir = Path("reports/monte_carlo_budget")
    summary_path = export_csv(
        summary_rows,
        output_dir / "budget_summary.csv",
    )
    game_path = export_csv(
        game_rows,
        output_dir / "budget_games.csv",
    )
    print_budget_comparison(summary_rows)
    print("\nGenerated files:")
    print(summary_path.resolve())
    print(game_path.resolve())


if __name__ == "__main__":
    main()

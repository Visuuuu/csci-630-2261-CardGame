import csv
import math
from pathlib import Path


# Two-sided 95% normal critical value.
Z_95 = 1.959963984540054


def wilson_confidence_interval(
    wins: int,
    games: int,
) -> tuple[float, float]:
    """Calculate a 95% Wilson confidence interval.
    Returns lower and upper bounds as percentages.
    """
    if games <= 0:
        raise ValueError("games must be positive.")
    if wins < 0 or wins > games:
        raise ValueError(
            "wins must be between 0 and games."
        )
    p = wins / games
    z = Z_95
    z_squared = z * z
    denominator = 1 + z_squared / games
    center = (
        p + z_squared / (2 * games)
    ) / denominator
    margin = (
        z
        * math.sqrt(
            p * (1 - p) / games
            + z_squared / (4 * games * games)
        )
        / denominator
    )
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return lower * 100, upper * 100


def analyze_tournament(
    results: dict,
    ruleset: str,
    mc_simulations: int,
    mc_depth: int,
) -> list[dict]:
    """Build a statistical summary for each AI strategy."""
    total_games = results["total_games"]
    if total_games <= 0:
        raise ValueError(
            "Tournament must contain at least one game."
        )
    rows = []
    for strategy, stats in results[
        "strategies"
    ].items():
        appearances = stats["appearances"]
        wins = stats["wins"]
        lower, upper = wilson_confidence_interval(
            wins,
            appearances,
        )
        rows.append({
            "ruleset": ruleset,
            "strategy": strategy,
            "total_games": total_games,
            "completed_games": results[
                "completed_games"
            ],
            "unfinished_games": results[
                "unfinished_games"
            ],
            "wins": wins,
            "appearances": appearances,
            "win_rate_pct": (
                100 * wins / appearances
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
            "mc_simulations": mc_simulations,
            "mc_depth": mc_depth,
        })
    return rows


def export_statistical_summary(
    rows: list[dict],
    output_path: str | Path,
) -> Path:
    """Save analyzed tournament results to CSV."""
    if not rows:
        raise ValueError("No statistical rows provided.")
    path = Path(output_path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    columns = [
        "ruleset",
        "strategy",
        "total_games",
        "completed_games",
        "unfinished_games",
        "wins",
        "appearances",
        "win_rate_pct",
        "ci_lower_pct",
        "ci_upper_pct",
        "average_hand_points",
        "average_decision_ms",
        "total_decisions",
        "mc_simulations",
        "mc_depth",
    ]
    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
        )
        writer.writeheader()
        writer.writerows(rows)
    return path

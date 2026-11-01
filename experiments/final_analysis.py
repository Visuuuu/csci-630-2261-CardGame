import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


REPORTS_DIR = Path("reports")
VALIDATION_CSV = (
    REPORTS_DIR
    / "validation"
    / "combined_statistical_summary.csv"
)
BUDGET_CSV = (
    REPORTS_DIR
    / "monte_carlo_budget"
    / "budget_summary.csv"
)
VERSIONS_CSV = (
    REPORTS_DIR
    / "monte_carlo_versions"
    / "version_summary.csv"
)
PAIRED_CSV = (
    REPORTS_DIR
    / "monte_carlo_versions"
    / "paired_games.csv"
)
OUTPUT_DIR = REPORTS_DIR / "final_analysis"
STRATEGIES = (
    "Random",
    "Greedy",
    "Heuristic",
    "Monte Carlo",
)


def read_csv(path):
    """Read a required experiment report."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Required report not found: {path}"
        )
    with path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError(
                f"CSV has no header: {path}"
            )
        rows = list(reader)
    if not rows:
        raise ValueError(
            f"CSV contains no data: {path}"
        )
    return rows


def numeric(row, key):
    """Convert and validate a finite numeric field."""
    if key not in row or row[key] in ("", None):
        raise ValueError(
            f"Missing numeric field: {key}"
        )
    try:
        value = float(row[key])
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Invalid value for {key}: {row[key]}"
        ) from error
    if not math.isfinite(value):
        raise ValueError(
            f"Non-finite value for {key}"
        )
    return value


def count(row, key):
    """Read an integer count, rejecting fractions."""
    value = numeric(row, key)
    if value < 0 or not value.is_integer():
        raise ValueError(
            f"{key} must be a nonnegative integer."
        )
    return int(value)


def validate_strategy_rows(rows, group_key):
    """Validate a complete four-strategy comparison."""
    groups = {}
    for row in rows:
        if group_key not in row:
            raise ValueError(
                f"Missing grouping field: {group_key}"
            )
        group = row[group_key]
        strategy = row.get("strategy")
        if not group or strategy not in STRATEGIES:
            raise ValueError(
                "Unknown group or strategy."
            )
        appearances = count(row, "appearances")
        wins = count(row, "wins")
        if appearances == 0 or wins > appearances:
            raise ValueError(
                "Invalid appearances or wins."
            )
        rate = numeric(row, "win_rate_pct")
        lower = numeric(row, "ci_lower_pct")
        upper = numeric(row, "ci_upper_pct")
        expected = 100.0 * wins / appearances
        if not math.isclose(
            rate,
            expected,
            abs_tol=1e-5,
        ):
            raise ValueError(
                "Win rate does not match wins/appearances."
            )
        # Allow tiny floating-point rounding differences.
        tolerance = 1e-8
        if not (
            -tolerance <= lower
            <= rate + tolerance
            and lower - tolerance
            <= upper
            <= 100 + tolerance
            and rate <= upper + tolerance
        ):
            raise ValueError(
                "Invalid confidence interval."
            )
        if numeric(row, "average_hand_points") < 0:
            raise ValueError(
                "Remaining points cannot be negative."
            )
        if numeric(row, "average_decision_ms") < 0:
            raise ValueError(
                "Decision time cannot be negative."
            )
        groups.setdefault(group, [])
        if strategy in {
            existing["strategy"]
            for existing in groups[group]
        }:
            raise ValueError(
                f"Duplicate strategy in group {group}."
            )
        groups[group].append(row)
    for group, members in groups.items():
        actual = {
            row["strategy"] for row in members
        }
        if actual != set(STRATEGIES):
            raise ValueError(
                f"Incomplete strategies for {group}."
            )
    return groups


def paired_outcomes(rows):
    """Count matched Monte Carlo win outcomes."""
    outcomes = {
        "both_win": 0,
        "v1_only": 0,
        "v2_only": 0,
        "neither_wins": 0,
    }
    game_numbers = set()
    point_differences = []
    for row in rows:
        game_number = count(row, "game_number")
        if game_number == 0 or game_number in game_numbers:
            raise ValueError(
                "Invalid or duplicate paired game number."
            )
        game_numbers.add(game_number)
        v1 = count(row, "v1_mc_won")
        v2 = count(row, "v2_mc_won")
        if v1 not in (0, 1) or v2 not in (0, 1):
            raise ValueError(
                "Paired win flags must be 0 or 1."
            )
        p1 = numeric(row, "v1_mc_points")
        p2 = numeric(row, "v2_mc_points")
        change = numeric(
            row,
            "points_change_v2_minus_v1",
        )
        if p1 < 0 or p2 < 0:
            raise ValueError(
                "Hand points cannot be negative."
            )
        if not math.isclose(
            p2 - p1,
            change,
            abs_tol=1e-8,
        ):
            raise ValueError(
                "Inconsistent paired point difference."
            )
        point_differences.append(change)
        if v1 and v2:
            outcomes["both_win"] += 1
        elif v1:
            outcomes["v1_only"] += 1
        elif v2:
            outcomes["v2_only"] += 1
        else:
            outcomes["neither_wins"] += 1
    outcomes["total_pairs"] = len(rows)
    outcomes["mean_points_change_v2_minus_v1"] = (
        sum(point_differences)
        / len(point_differences)
    )
    return outcomes


def find_mc_row(rows):
    """Return the Monte Carlo row within a group."""
    return next(
        row for row in rows
        if row["strategy"] == "Monte Carlo"
    )


def analyze_results(
    validation_rows,
    budget_rows,
    version_rows,
    paired_rows,
):
    """Validate data and construct the final analysis."""
    validation = validate_strategy_rows(
        validation_rows,
        "ruleset",
    )
    budgets = validate_strategy_rows(
        budget_rows,
        "mc_simulations",
    )
    versions = validate_strategy_rows(
        version_rows,
        "version",
    )
    if len(validation) != 2:
        raise ValueError(
            "Expected two UNO ruleset groups."
        )
    if set(budgets) != {"25", "50", "100"}:
        raise ValueError(
            "Expected budgets 25, 50 and 100."
        )
    if set(versions) != {"V1", "V2"}:
        raise ValueError(
            "Expected Monte Carlo V1 and V2."
        )
    if len(paired_rows) != count(
        find_mc_row(versions["V1"]),
        "appearances",
    ):
        raise ValueError(
            "Paired-game count does not match V1."
        )
    if len(paired_rows) != count(
        find_mc_row(versions["V2"]),
        "appearances",
    ):
        raise ValueError(
            "Paired-game count does not match V2."
        )
    outcomes = paired_outcomes(paired_rows)
    v1 = find_mc_row(versions["V1"])
    v2 = find_mc_row(versions["V2"])
    if (
        outcomes["both_win"] + outcomes["v1_only"]
        != count(v1, "wins")
        or outcomes["both_win"] + outcomes["v2_only"]
        != count(v2, "wins")
    ):
        raise ValueError(
            "Paired wins disagree with version summary."
        )
    budget_mc = {
        int(budget): find_mc_row(rows)
        for budget, rows in budgets.items()
    }
    best_win_budget = max(
        budget_mc,
        key=lambda b: (
            numeric(budget_mc[b], "win_rate_pct"),
            -b,
        ),
    )
    fastest_budget = min(
        budget_mc,
        key=lambda b: (
            numeric(
                budget_mc[b],
                "average_decision_ms",
            ),
            b,
        ),
    )
    return {
        "validation": validation,
        "budgets": budgets,
        "versions": versions,
        "paired": outcomes,
        "comparison": {
            "v1_win_rate_pct": numeric(
                v1, "win_rate_pct"
            ),
            "v2_win_rate_pct": numeric(
                v2, "win_rate_pct"
            ),
            "win_rate_change_pp": (
                numeric(v2, "win_rate_pct")
                - numeric(v1, "win_rate_pct")
            ),
            "decision_time_change_ms": (
                numeric(v2, "average_decision_ms")
                - numeric(v1, "average_decision_ms")
            ),
            "hand_points_change": (
                numeric(v2, "average_hand_points")
                - numeric(v1, "average_hand_points")
            ),
            "highest_observed_win_rate_budget": (
                best_win_budget
            ),
            "lowest_observed_decision_time_budget": (
                fastest_budget
            ),
        },
    }


def format_table(rows, columns):
    """Format Markdown table rows."""
    lines = [
        "| " + " | ".join(
            heading for heading, _ in columns
        ) + " |",
        "| " + " | ".join(
            "---" for _ in columns
        ) + " |",
    ]
    for row in rows:
        cells = []
        for _, field in columns:
            value = row.get(field, "")
            if field in (
                "win_rate_pct",
                "ci_lower_pct",
                "ci_upper_pct",
                "average_hand_points",
                "average_decision_ms",
            ):
                value = f"{numeric(row, field):.2f}"
            cells.append(str(value))
        lines.append(
            "| " + " | ".join(cells) + " |"
        )
    return "\n".join(lines)


def build_markdown_report(analysis):
    """Create a report using measured results only."""
    lines = [
        "# Comparative AI Agents for a Strategic Card Game",
        "",
        "## Final Experimental Results and Analysis",
        "",
        "Generated from the project's existing CSV reports.",
        "",
        "### 1. Four-agent comparison by ruleset",
        "",
    ]
    columns = [
        ("Strategy", "strategy"),
        ("Wins", "wins"),
        ("Win rate (%)", "win_rate_pct"),
        ("CI low (%)", "ci_lower_pct"),
        ("CI high (%)", "ci_upper_pct"),
        ("Avg hand points", "average_hand_points"),
        ("Avg decision (ms)", "average_decision_ms"),
    ]
    for ruleset, rows in sorted(
        analysis["validation"].items()
    ):
        lines.extend([
            f"#### {ruleset}",
            "",
            format_table(rows, columns),
            "",
        ])
    lines.extend([
        "Results from the two rulesets are shown "
        "separately because the legal card set differs.",
        "",
        "### 2. Monte Carlo simulation budget",
        "",
    ])
    budget_rows = [
        find_mc_row(analysis["budgets"][str(b)])
        for b in (25, 50, 100)
    ]
    for budget, row in zip(
        (25, 50, 100), budget_rows
    ):
        row["budget_label"] = budget
    lines.extend([
        format_table(
            budget_rows,
            [
                ("Simulations", "budget_label"),
                ("Wins", "wins"),
                ("Win rate (%)", "win_rate_pct"),
                ("Avg points", "average_hand_points"),
                ("Avg decision (ms)",
                 "average_decision_ms"),
            ],
        ),
        "",
        "Highest observed win-rate budget: "
        f"**{analysis['comparison']['highest_observed_win_rate_budget']}**.",
        "",
        "Lowest observed decision-time budget: "
        f"**{analysis['comparison']['lowest_observed_decision_time_budget']}**.",
        "",
        "These are descriptive rankings, not proof "
        "that a particular simulation budget is optimal.",
        "",
        "### 3. Monte Carlo V1 versus V2",
        "",
    ])
    version_rows = [
        find_mc_row(analysis["versions"][version])
        for version in ("V1", "V2")
    ]
    for version, row in zip(
        ("V1", "V2"), version_rows
    ):
        row["version_label"] = version
    lines.extend([
        format_table(
            version_rows,
            [
                ("Version", "version_label"),
                ("Wins", "wins"),
                ("Win rate (%)", "win_rate_pct"),
                ("CI low (%)", "ci_lower_pct"),
                ("CI high (%)", "ci_upper_pct"),
                ("Avg points", "average_hand_points"),
                ("Avg decision (ms)",
                 "average_decision_ms"),
            ],
        ),
        "",
    ])
    comparison = analysis["comparison"]
    paired = analysis["paired"]
    lines.extend([
        "Observed V2 minus V1 differences:",
        "",
        f"- Win rate: "
        f"{comparison['win_rate_change_pp']:+.2f} "
        "percentage points.",
        f"- Average remaining hand points: "
        f"{comparison['hand_points_change']:+.2f}.",
        f"- Average decision time: "
        f"{comparison['decision_time_change_ms']:+.4f} ms.",
        "",
        "#### Matched initial conditions",
        "",
        f"- Both versions won: {paired['both_win']}",
        f"- Only V1 won: {paired['v1_only']}",
        f"- Only V2 won: {paired['v2_only']}",
        f"- Neither version won: {paired['neither_wins']}",
        f"- Total matched pairs: {paired['total_pairs']}",
        "",
        "A negative remaining-points difference favors "
        "V2, while a positive decision-time difference "
        "means V2 required more computation.",
        "",
        "### 4. Interpretation and limitations",
        "",
        "1. The four primary AI strategies were "
        "Random, Greedy, Heuristic and Monte Carlo.",
        "2. Win rate, remaining hand points and "
        "decision time are different performance "
        "dimensions; none alone establishes overall "
        "algorithm superiority.",
        "3. The win-rate intervals are Wilson 95% "
        "intervals for individual observed rates. "
        "They are not confidence intervals for the "
        "difference between two strategies.",
        "4. Matches using shared starting seeds can "
        "diverge after different agent decisions. "
        "Matched seeds control initial conditions, "
        "not entire trajectories.",
        "5. Monte Carlo V1 uses approximate futures. "
        "V2 samples legal hypothetical opponent moves "
        "but does not model persistent full four-player "
        "hidden hands or all action-card effects.",
        "6. Observed decision times depend on the "
        "computer and runtime conditions.",
        "7. Small tournament samples limit the "
        "strength of statistical conclusions. "
        "Further independent tournament blocks "
        "would strengthen future research.",
        "",
        "### 5. Supporting figures",
        "",
        "- `reports/monte_carlo_budget/charts/`",
        "- `reports/monte_carlo_versions/charts/`",
        "",
        "The figures and tables should be reviewed "
        "together when preparing the final presentation.",
        "",
    ])
    return "\n".join(lines)


def export_final_analysis(analysis, output_dir):
    """Save Markdown and JSON final results."""
    output_dir = Path(output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    markdown_path = (
        output_dir / "final_research_summary.md"
    )
    json_path = (
        output_dir / "final_research_data.json"
    )
    markdown_path.write_text(
        build_markdown_report(analysis),
        encoding="utf-8",
    )
    payload = {
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "comparison": analysis["comparison"],
        "paired": analysis["paired"],
    }
    json_path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    return markdown_path, json_path


def main():
    analysis = analyze_results(
        validation_rows=read_csv(VALIDATION_CSV),
        budget_rows=read_csv(BUDGET_CSV),
        version_rows=read_csv(VERSIONS_CSV),
        paired_rows=read_csv(PAIRED_CSV),
    )
    markdown_path, json_path = (
        export_final_analysis(
            analysis,
            OUTPUT_DIR,
        )
    )
    print("FINAL EXPERIMENTAL ANALYSIS")
    print("=" * 55)
    comparison = analysis["comparison"]
    print(
        "Monte Carlo V1 win rate: "
        f"{comparison['v1_win_rate_pct']:.2f}%"
    )
    print(
        "Monte Carlo V2 win rate: "
        f"{comparison['v2_win_rate_pct']:.2f}%"
    )
    print(
        "Observed V2-V1 change: "
        f"{comparison['win_rate_change_pp']:+.2f} pp"
    )
    print("\nReports generated:")
    print(markdown_path.resolve())
    print(json_path.resolve())


if __name__ == "__main__":
    main()

import csv
import math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


REPORT_DIR = Path("reports/monte_carlo_versions")
SUMMARY_CSV = REPORT_DIR / "version_summary.csv"
PAIRED_CSV = REPORT_DIR / "paired_games.csv"
CHART_DIR = REPORT_DIR / "charts"
VERSIONS = ("V1", "V2")


def load_version_summary(path: str | Path) -> list[dict]:
    """Load and validate the two Monte Carlo summary rows."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Version summary not found: {path}"
        )
    required = {
        "version",
        "strategy",
        "wins",
        "appearances",
        "win_rate_pct",
        "ci_lower_pct",
        "ci_upper_pct",
        "average_hand_points",
        "average_decision_ms",
    }
    rows = []
    with path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Missing summary columns: {sorted(missing)}"
            )
        for raw in reader:
            if raw["strategy"] != "Monte Carlo":
                continue
            try:
                row = {
                    "version": raw["version"],
                    "wins": int(raw["wins"]),
                    "appearances": int(raw["appearances"]),
                    "win_rate_pct": float(
                        raw["win_rate_pct"]
                    ),
                    "ci_lower_pct": float(
                        raw["ci_lower_pct"]
                    ),
                    "ci_upper_pct": float(
                        raw["ci_upper_pct"]
                    ),
                    "average_hand_points": float(
                        raw["average_hand_points"]
                    ),
                    "average_decision_ms": float(
                        raw["average_decision_ms"]
                    ),
                }
            except (ValueError, TypeError) as error:
                raise ValueError(
                    "Invalid numeric summary value."
                ) from error
            if row["version"] not in VERSIONS:
                raise ValueError("Unknown Monte Carlo version.")
            if not (
                0 <= row["wins"] <= row["appearances"]
                and row["appearances"] > 0
            ):
                raise ValueError(
                    "Invalid win count or appearances."
                )
            numeric = (
                row["win_rate_pct"],
                row["ci_lower_pct"],
                row["ci_upper_pct"],
                row["average_hand_points"],
                row["average_decision_ms"],
            )
            if not all(math.isfinite(x) for x in numeric):
                raise ValueError("Metrics must be finite.")
            if not (
                0 <= row["ci_lower_pct"]
                <= row["win_rate_pct"]
                <= row["ci_upper_pct"]
                <= 100
            ):
                raise ValueError(
                    "Invalid confidence interval."
                )
            if (
                row["average_hand_points"] < 0
                or row["average_decision_ms"] < 0
            ):
                raise ValueError(
                    "Points and times cannot be negative."
                )
            expected_rate = (
                100 * row["wins"] / row["appearances"]
            )
            if not math.isclose(
                row["win_rate_pct"],
                expected_rate,
                abs_tol=1e-6,
            ):
                raise ValueError(
                    "Win rate does not match wins/appearances."
                )
            rows.append(row)
    by_version = {
        row["version"]: row for row in rows
    }
    if (
        len(rows) != 2
        or set(by_version) != set(VERSIONS)
    ):
        raise ValueError(
            "Expected exactly one Monte Carlo "
            "summary row for V1 and V2."
        )
    return [by_version[name] for name in VERSIONS]


def load_paired_games(path: str | Path) -> list[dict]:
    """Load paired game results for V1 and V2."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Paired game report not found: {path}"
        )
    required = {
        "game_number",
        "mc_seat",
        "v1_mc_won",
        "v2_mc_won",
        "v1_mc_points",
        "v2_mc_points",
        "points_change_v2_minus_v1",
    }
    rows = []
    with path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Missing paired columns: {sorted(missing)}"
            )
        for raw in reader:
            try:
                row = {
                    key: int(raw[key])
                    for key in required
                }
            except (ValueError, TypeError) as error:
                raise ValueError(
                    "Invalid numeric paired-game value."
                ) from error
            if (
                row["v1_mc_won"] not in (0, 1)
                or row["v2_mc_won"] not in (0, 1)
            ):
                raise ValueError(
                    "Win flags must be 0 or 1."
                )
            if (
                row["game_number"] <= 0
                or row["mc_seat"] not in range(4)
                or row["v1_mc_points"] < 0
                or row["v2_mc_points"] < 0
            ):
                raise ValueError(
                    "Invalid game number, seat, or points."
                )
            expected_change = (
                row["v2_mc_points"]
                - row["v1_mc_points"]
            )
            if (
                row["points_change_v2_minus_v1"]
                != expected_change
            ):
                raise ValueError(
                    "Paired point difference is inconsistent."
                )

            rows.append(row)
    if not rows:
        raise ValueError("No paired games found.")
    game_numbers = [
        row["game_number"] for row in rows
    ]
    if len(game_numbers) != len(set(game_numbers)):
        raise ValueError("Duplicate game number found.")
    rows.sort(key=lambda row: row["game_number"])
    return rows


def summarize_paired_outcomes(
    rows: list[dict],
) -> dict[str, int]:
    """Count four possible matched win outcomes."""
    counts = {
        "Both win": 0,
        "V1 only": 0,
        "V2 only": 0,
        "Neither": 0,
    }
    for row in rows:
        v1 = bool(row["v1_mc_won"])
        v2 = bool(row["v2_mc_won"])
        if v1 and v2:
            counts["Both win"] += 1
        elif v1:
            counts["V1 only"] += 1
        elif v2:
            counts["V2 only"] += 1
        else:
            counts["Neither"] += 1
    return counts


class MonteCarloVersionPlotter:
    """Create comparison charts from measured V1/V2 data."""
    def __init__(
        self,
        output_dir: str | Path = CHART_DIR,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _save(self, fig, filename: str) -> Path:
        path = self.output_dir / filename
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return path

    @staticmethod
    def _label_bars(ax, bars, values, fmt: str):
        for bar, value in zip(bars, values):
            ax.annotate(
                format(value, fmt),
                (
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                ),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
            )

    def plot_win_rates(
        self,
        summary: list[dict],
    ) -> Path:
        """Compare win rates with Wilson intervals."""
        values = [
            row["win_rate_pct"] for row in summary
        ]
        lower = [
            row["win_rate_pct"] - row["ci_lower_pct"]
            for row in summary
        ]
        upper = [
            row["ci_upper_pct"] - row["win_rate_pct"]
            for row in summary
        ]
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.errorbar(
            VERSIONS,
            values,
            yerr=[lower, upper],
            fmt="o",
            capsize=8,
            markersize=9,
        )
        ax.set_title(
            "Monte Carlo V1 vs V2: Win Rate"
        )
        ax.set_ylabel("Win Rate (%)")
        ax.set_ylim(0, 100)
        ax.grid(axis="y", alpha=0.25)
        return self._save(
            fig,
            "version_win_rate.png",
        )

    def plot_remaining_points(
        self,
        summary: list[dict],
    ) -> Path:
        """Compare average remaining hand points."""
        values = [
            row["average_hand_points"]
            for row in summary
        ]
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(VERSIONS, values)
        ax.set_title(
            "Monte Carlo V1 vs V2: Remaining Hand Points"
        )
        ax.set_ylabel("Average Remaining Points")
        ax.set_ylim(0, max(max(values) * 1.25, 1))
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
        self._label_bars(
            ax, bars, values, ".2f"
        )
        return self._save(
            fig,
            "version_remaining_points.png",
        )

    def plot_decision_time(
        self,
        summary: list[dict],
    ) -> Path:
        """Compare average decision times."""
        values = [
            row["average_decision_ms"]
            for row in summary
        ]
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(VERSIONS, values)
        ax.set_title(
            "Monte Carlo V1 vs V2: Decision Time"
        )
        ax.set_ylabel("Milliseconds per Decision")
        ax.set_ylim(
            0,
            max(max(values) * 1.25, 0.001),
        )
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
        self._label_bars(
            ax, bars, values, ".4f"
        )
        return self._save(
            fig,
            "version_decision_time.png",
        )

    def plot_paired_outcomes(
        self,
        paired: list[dict],
    ) -> Path:
        """Show matched-game win outcomes."""
        counts = summarize_paired_outcomes(paired)
        labels = list(counts)
        values = list(counts.values())
        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.bar(labels, values)
        ax.set_title(
            "Monte Carlo V1 vs V2: Matched-Game Outcomes"
        )
        ax.set_ylabel("Number of Matched Game Pairs")
        ax.set_ylim(
            0,
            max(max(values) * 1.25, 1),
        )
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
        self._label_bars(
            ax, bars, values, "d"
        )
        return self._save(
            fig,
            "version_paired_outcomes.png",
        )

    def generate_all(
        self,
        summary: list[dict],
        paired: list[dict],
    ) -> list[Path]:
        """Generate the four V1/V2 charts."""
        return [
            self.plot_win_rates(summary),
            self.plot_remaining_points(summary),
            self.plot_decision_time(summary),
            self.plot_paired_outcomes(paired),
        ]


def main():
    summary = load_version_summary(SUMMARY_CSV)
    paired = load_paired_games(PAIRED_CSV)
    plotter = MonteCarloVersionPlotter()
    paths = plotter.generate_all(summary, paired)
    print("\nMonte Carlo V1 vs V2 comparison")
    for row in summary:
        print(
            f"{row['version']}: "
            f"wins={row['wins']}, "
            f"win rate={row['win_rate_pct']:.2f}%, "
            f"points={row['average_hand_points']:.2f}, "
            f"decision time={row['average_decision_ms']:.4f} ms"
        )
    print("\nMatched-game outcomes:")
    for outcome, count in summarize_paired_outcomes(
        paired
    ).items():
        print(f"  {outcome}: {count}")
    print("\nGenerated charts:")
    for path in paths:
        print(f"  {path.resolve()}")


if __name__ == "__main__":
    main()

import csv
import math
from pathlib import Path
import matplotlib
# Save images without opening a graphical window.
matplotlib.use("Agg")
import matplotlib.pyplot as plt


DEFAULT_INPUT = Path(
    "reports/monte_carlo_budget/budget_summary.csv"
)

DEFAULT_OUTPUT = Path(
    "reports/monte_carlo_budget/charts"
)


def load_monte_carlo_results(csv_path: str | Path) -> list[dict]:
    """Load and validate Monte Carlo budget summary data."""
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Budget summary not found: {path}"
        )
    required_columns = {
        "mc_simulations",
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
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)
        if not required_columns.issubset(
            set(reader.fieldnames or [])
        ):
            missing = required_columns - set(
                reader.fieldnames or []
            )
            raise ValueError(
                f"Missing CSV columns: {sorted(missing)}"
            )
        for raw in reader:
            if raw["strategy"] != "Monte Carlo":
                continue
            try:
                row = {
                    "budget": int(raw["mc_simulations"]),
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
                    "Invalid numeric value in "
                    "Monte Carlo summary row."
                ) from error
            if row["budget"] <= 0:
                raise ValueError(
                    "Simulation budget must be positive."
                )
            if not (
                0 <= row["wins"] <= row["appearances"]
                and row["appearances"] > 0
            ):
                raise ValueError(
                    "Invalid wins or appearances."
                )
            numeric_values = (
                row["win_rate_pct"],
                row["ci_lower_pct"],
                row["ci_upper_pct"],
                row["average_hand_points"],
                row["average_decision_ms"],
            )
            if not all(
                math.isfinite(value)
                for value in numeric_values
            ):
                raise ValueError(
                    "Metrics must contain finite numbers."
                )
            if not (
                0 <= row["ci_lower_pct"]
                <= row["win_rate_pct"]
                <= row["ci_upper_pct"]
                <= 100
            ):
                raise ValueError(
                    "Invalid win-rate confidence interval."
                )
            if (
                row["average_hand_points"] < 0
                or row["average_decision_ms"] < 0
            ):
                raise ValueError(
                    "Point totals and timings "
                    "cannot be negative."
                )
            rows.append(row)
    if not rows:
        raise ValueError(
            "No Monte Carlo results found in CSV."
        )
    rows.sort(key=lambda row: row["budget"])
    budgets = [row["budget"] for row in rows]
    if len(budgets) != len(set(budgets)):
        raise ValueError(
            "Duplicate Monte Carlo budget rows found."
        )
    return rows


class MonteCarloBudgetPlotter:
    """Create charts for a Monte Carlo budget study."""
    def __init__(
        self,
        output_dir: str | Path = DEFAULT_OUTPUT,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
    @staticmethod
    def _setup_axis(ax, title, ylabel):
        ax.set_title(title, fontsize=14, pad=14)
        ax.set_xlabel("Simulations per Candidate")
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)

    def _save(self, fig, filename: str) -> Path:
        path = self.output_dir / filename
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return path

    def plot_win_rate(self, rows: list[dict]) -> Path:
        """Plot win rates with Wilson 95% intervals."""
        budgets = [row["budget"] for row in rows]
        rates = [
            row["win_rate_pct"] for row in rows
        ]
        lower_errors = [
            row["win_rate_pct"] - row["ci_lower_pct"]
            for row in rows
        ]
        upper_errors = [
            row["ci_upper_pct"] - row["win_rate_pct"]
            for row in rows
        ]
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.errorbar(
            budgets,
            rates,
            yerr=[lower_errors, upper_errors],
            fmt="o-",
            capsize=7,
            linewidth=2,
            markersize=7,
        )
        self._setup_axis(
            ax,
            "Monte Carlo Win Rate by Simulation Budget",
            "Win Rate (%)",
        )
        ax.set_xticks(budgets)
        ax.set_ylim(0, 100)
        return self._save(
            fig,
            "budget_win_rate.png",
        )

    def plot_remaining_points(
        self,
        rows: list[dict],
    ) -> Path:
        """Plot average remaining hand points."""
        labels = [
            str(row["budget"]) for row in rows
        ]
        values = [
            row["average_hand_points"]
            for row in rows
        ]
        fig, ax = plt.subplots(figsize=(9, 5.5))
        bars = ax.bar(labels, values)
        self._setup_axis(
            ax,
            "Remaining Hand Points by Monte Carlo Budget",
            "Average Remaining Hand Points",
        )
        ax.set_ylim(
            0,
            max(max(values) * 1.2, 1),
        )
        for bar, value in zip(bars, values):
            ax.annotate(
                f"{value:.2f}",
                (
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                ),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
            )
        return self._save(
            fig,
            "budget_remaining_points.png",
        )

    def plot_decision_time(
        self,
        rows: list[dict],
    ) -> Path:
        """Plot average AI decision time."""
        labels = [
            str(row["budget"]) for row in rows
        ]
        values = [
            row["average_decision_ms"]
            for row in rows
        ]
        fig, ax = plt.subplots(figsize=(9, 5.5))
        bars = ax.bar(labels, values)
        self._setup_axis(
            ax,
            "Monte Carlo Decision Time by Budget",
            "Average Decision Time (ms)",
        )
        ax.set_ylim(
            0,
            max(max(values) * 1.2, 0.001),
        )
        for bar, value in zip(bars, values):
            ax.annotate(
                f"{value:.3f} ms",
                (
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                ),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
            )
        return self._save(
            fig,
            "budget_decision_time.png",
        )

    def plot_tradeoff(
        self,
        rows: list[dict],
    ) -> Path:
        """Compare win rate against decision time."""
        times = [
            row["average_decision_ms"]
            for row in rows
        ]
        rates = [
            row["win_rate_pct"]
            for row in rows
        ]
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.scatter(
            times,
            rates,
            s=100,
            zorder=3,
        )
        for row in rows:
            ax.annotate(
                f"{row['budget']} simulations",
                (
                    row["average_decision_ms"],
                    row["win_rate_pct"],
                ),
                xytext=(8, 8),
                textcoords="offset points",
            )
        ax.set_title(
            "Monte Carlo: Win Rate vs. Decision Time",
            fontsize=14,
            pad=14,
        )
        ax.set_xlabel("Average Decision Time (ms)")
        ax.set_ylabel("Win Rate (%)")
        ax.set_ylim(0, 100)
        ax.set_xlim(
            left=0,
            right=max(max(times) * 1.35, 0.001),
        )
        ax.grid(alpha=0.25)
        return self._save(
            fig,
            "budget_tradeoff.png",
        )

    def generate_all(self, rows: list[dict]) -> list[Path]:
        """Create all four comparison charts."""
        return [
            self.plot_win_rate(rows),
            self.plot_remaining_points(rows),
            self.plot_decision_time(rows),
            self.plot_tradeoff(rows),
        ]


def main():
    rows = load_monte_carlo_results(
        DEFAULT_INPUT
    )
    print("\nLoaded Monte Carlo budget results:")
    for row in rows:
        print(
            f"Budget {row['budget']:>3}: "
            f"Win rate = {row['win_rate_pct']:.2f}%, "
            f"Points = {row['average_hand_points']:.2f}, "
            f"Time = {row['average_decision_ms']:.4f} ms"
        )
    plotter = MonteCarloBudgetPlotter()
    paths = plotter.generate_all(rows)
    print("\nGenerated comparison charts:")
    for path in paths:
        print(f"  {path.resolve()}")


if __name__ == "__main__":
    main()

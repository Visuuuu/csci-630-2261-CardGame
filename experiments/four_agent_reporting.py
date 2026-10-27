import csv
from pathlib import Path
import matplotlib
# Save charts without opening GUI windows.
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class FourAgentReporter:
    """Generate CSV reports and charts for four AI agents."""
    STRATEGIES = (
        "Random",
        "Greedy",
        "Heuristic",
        "Monte Carlo",
    )
    def __init__(self, output_dir="reports/four_agents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def export_strategy_summary(self, results: dict) -> Path:
        """Export aggregated strategy statistics."""
        output_path = (
            self.output_dir / "strategy_summary.csv"
        )
        columns = [
            "strategy",
            "wins",
            "win_share_pct",
            "win_rate_per_appearance_pct",
            "average_hand_points",
            "average_decision_ms",
            "appearances",
            "decisions",
        ]
        with output_path.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file, fieldnames=columns
            )
            writer.writeheader()
            for strategy in self.STRATEGIES:
                stats = results["strategies"][strategy]
                writer.writerow({
                    "strategy": strategy,
                    **{
                        column: (
                            stats[column]
                            if stats[column] is not None
                            else ""
                        )
                        for column in columns[1:]
                    },
                })
        return output_path

    def export_game_results(self, results: dict) -> Path:
        """Export each player-game result with seat position."""
        output_path = (
            self.output_dir / "game_results.csv"
        )
        with output_path.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow([
                "game_number",
                "completed",
                "winner",
                "turns",
                "seat",
                "strategy",
                "won",
                "remaining_hand_points",
            ])
            for game in results["games"]:
                for seat, strategy in enumerate(
                    game["lineup"]
                ):
                    writer.writerow([
                        game["game_number"],
                        game["completed"],
                        game["winner"] or "",
                        game["turns"],
                        seat,
                        strategy,
                        int(
                            game["completed"]
                            and game["winner"] == strategy
                        ),
                        game["hand_points"][strategy],
                    ])
        return output_path

    def _create_bar_chart(
        self,
        values: list[float],
        title: str,
        ylabel: str,
        filename: str,
        percentage: bool = False,
    ) -> Path:
        """Create and save a four-strategy bar chart."""
        fig, ax = plt.subplots(figsize=(9, 5.5))
        labels = list(self.STRATEGIES)
        bars = ax.bar(labels, values)
        ax.set_title(title, fontsize=14)
        ax.set_xlabel("AI Strategy")
        ax.set_ylabel(ylabel)
        upper_limit = (
            100 if percentage
            else max(max(values, default=0) * 1.2, 1)
        )
        ax.set_ylim(0, upper_limit)
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
        for bar, value in zip(bars, values):
            label = (
                f"{value:.2f}%"
                if percentage
                else f"{value:.4f}"
            )
            ax.annotate(
                label,
                xy=(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                ),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
            )
        fig.tight_layout()
        path = self.output_dir / filename
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return path

    def create_charts(self, results: dict) -> list[Path]:
        """Generate charts from measured strategy statistics."""
        strategies = results["strategies"]
        paths = []
        def values_for(metric):
            return [
                strategies[name][metric]
                for name in self.STRATEGIES
            ]
        # Win share is undefined if no match finished.
        if results["completed_games"] > 0:
            paths.append(
                self._create_bar_chart(
                    values_for("win_share_pct"),
                    "UNO AI: Completed-Game Win Share",
                    "Win Share (%)",
                    "win_share.png",
                    percentage=True,
                )
            )
        paths.append(
            self._create_bar_chart(
                values_for(
                    "win_rate_per_appearance_pct"
                ),
                "UNO AI: Win Rate per Appearance",
                "Win Rate (%)",
                "win_rate.png",
                percentage=True,
            )
        )
        paths.append(
            self._create_bar_chart(
                values_for("average_hand_points"),
                "UNO AI: Average Remaining Hand Points",
                "Remaining Hand Points",
                "remaining_points.png",
            )
        )
        # Skip undefined timings if no decisions exist.
        decision_times = values_for(
            "average_decision_ms"
        )
        if all(value is not None for value in decision_times):
            paths.append(
                self._create_bar_chart(
                    decision_times,
                    "UNO AI: Average Decision Time",
                    "Milliseconds per Decision",
                    "decision_time.png",
                )
            )
        return paths

    def generate_report(self, results: dict) -> list[Path]:
        """Generate all CSV and PNG report files."""
        paths = [
            self.export_strategy_summary(results),
            self.export_game_results(results),
        ]
        paths.extend(self.create_charts(results))
        print("\nGenerated experiment reports:")
        for path in paths:
            print(f"  {path.resolve()}")
        return paths
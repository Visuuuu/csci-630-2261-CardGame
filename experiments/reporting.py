import csv
from pathlib import Path
import matplotlib
# Generate images without requiring a GUI window.
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class ExperimentReporter:
    """Export UNO experiment results and charts."""
    def __init__(self, output_dir="reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def export_strategy_summary(self, results: dict):
        """Save aggregated strategy metrics to CSV."""
        output_path = (
            self.output_dir / "strategy_summary.csv"
        )
        fieldnames = [
            "strategy",
            "wins",
            "win_share_pct",
            "average_hand_points",
            "average_decision_ms",
            "decisions",
            "appearances",
        ]
        with output_path.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file, fieldnames=fieldnames
            )
            writer.writeheader()
            for strategy, stats in results[
                "strategies"
            ].items():
                writer.writerow({
                    "strategy": strategy,
                    **{
                        field: stats[field]
                        for field in fieldnames[1:]
                    },
                })
        return output_path

    def export_game_results(self, results: dict):
        """Save per-player results from every match."""
        output_path = (
            self.output_dir / "game_results.csv"
        )
        # Derive strategy from the Step 14 experiment.
        from experiments.compare_agents import (
            AgentExperiment,
        )
        strategy_lookup = {
            name: strategy
            for name, strategy
            in AgentExperiment.BASE_LINEUP
        }
        with output_path.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow([
                "game_number",
                "completed",
                "winner",
                "winner_strategy",
                "turns",
                "player_name",
                "strategy",
                "remaining_hand_points",
            ])
            for game in results["games"]:
                for name, points in game[
                    "hand_points"
                ].items():
                    writer.writerow([
                        game["game_number"],
                        game["completed"],
                        game["winner"] or "",
                        game["winner_strategy"] or "",
                        game["turns"],
                        name,
                        strategy_lookup[name],
                        points,
                    ])
        return output_path

    def _create_bar_chart(
        self,
        labels,
        values,
        title,
        ylabel,
        filename,
        percentage=False,
    ):
        """Generate a bar chart and save it as PNG."""
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(
            labels,
            values,
            color=["#4472C4", "#ED7D31"][:len(labels)],
        )
        ax.set_title(title, fontsize=14)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("AI Strategy")
        ax.set_ylim(
            bottom=0,
            top=100 if percentage
            else max(max(values, default=0) * 1.2, 1),
        )
        for bar, value in zip(bars, values):
            label = (
                f"{value:.2f}%"
                if percentage
                else f"{value:.4f}"
            )
            ax.annotate(
                label,
                (
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                ),
                ha="center",
                va="bottom",
                xytext=(0, 4),
                textcoords="offset points",
            )
        fig.tight_layout()
        output_path = self.output_dir / filename
        fig.savefig(output_path, dpi=200)
        plt.close(fig)
        return output_path

    def create_charts(self, results: dict):
        """Create charts for all three comparison metrics."""
        strategies = results["strategies"]
        labels = list(strategies.keys())
        if results["completed_games"] > 0:
            win_share = [
                strategies[name]["win_share_pct"]
                for name in labels
            ]
            self._create_bar_chart(
                labels,
                win_share,
                "UNO AI: Win Share Comparison",
                "Win Share (%)",
                "win_share.png",
                percentage=True,
            )
        hand_points = [
            strategies[name]["average_hand_points"]
            for name in labels
        ]
        self._create_bar_chart(
            labels,
            hand_points,
            "UNO AI: Average Remaining Hand Points",
            "Average Hand Points",
            "remaining_points.png",
        )
        decision_times = [
            strategies[name]["average_decision_ms"]
            for name in labels
        ]
        self._create_bar_chart(
            labels,
            decision_times,
            "UNO AI: Average Decision Time",
            "Time (milliseconds)",
            "decision_time.png",
        )

    def generate_report(self, results: dict):
        """Export all reports from one experiment."""
        self.export_strategy_summary(results)
        self.export_game_results(results)
        self.create_charts(results)
        print(
            f"\nExperiment reports saved to: "
            f"{self.output_dir.resolve()}"
        )
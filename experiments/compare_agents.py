from collections import defaultdict
from dataclasses import dataclass
from agents.greedy_agent import GreedyAgent
from agents.random_agent import RandomAgent
from interface.game_controller import GameController


@dataclass(frozen=True)
class ExperimentConfig:
    """Configuration for comparing UNO agents."""
    num_games: int = 40
    max_turns: int = 1000
    base_seed: int = 42


class AgentExperiment:
    """Run repeated Random-versus-Greedy UNO matches."""
    STRATEGIES = ("Random", "Greedy")
    # Each match has two agents of each strategy.
    BASE_LINEUP = (
        ("Random 1", "Random"),
        ("Greedy 1", "Greedy"),
        ("Random 2", "Random"),
        ("Greedy 2", "Greedy"),
    )
    def __init__(self, config: ExperimentConfig):
        if config.num_games <= 0:
            raise ValueError("num_games must be positive.")
        if config.max_turns <= 0:
            raise ValueError("max_turns must be positive.")
        self.config = config

    def _get_lineup(self, game_index: int):
        """Rotate agents through all four positions."""
        shift = game_index % 4
        return (
            self.BASE_LINEUP[-shift:]
            + self.BASE_LINEUP[:-shift]
            if shift
            else self.BASE_LINEUP
        )

    def _create_controller(
        self,
        game_index: int,
    ) -> GameController:
        """Create fresh agents and a fresh game."""
        lineup = self._get_lineup(game_index)
        agents = []
        names = []
        for agent_name, strategy in lineup:
            names.append(agent_name)
            if strategy == "Random":
                # Reproducible, independent agent seeds.
                agent_number = (
                    1 if agent_name == "Random 1" else 2
                )
                agent_seed = (
                    self.config.base_seed * 100_000
                    + game_index * 10
                    + agent_number
                )
                agents.append(
                    RandomAgent(seed=agent_seed)
                )
            else:
                agents.append(GreedyAgent())

        # Keep one deck seed per game.
        deck_seed = self.config.base_seed + game_index
        return GameController(
            agents=agents,
            player_names=names,
            seed=deck_seed,
        )

    def run(self, verbose: bool = True) -> dict:
        """Run all games and aggregate their metrics."""
        wins = defaultdict(int)
        hand_points_total = defaultdict(int)
        player_appearances = defaultdict(int)
        decision_time_total = defaultdict(float)
        decision_count = defaultdict(int)

        completed_games = 0
        unfinished_games = 0
        total_turns = 0
        game_records = []

        name_to_strategy = {
            name: strategy
            for name, strategy in self.BASE_LINEUP
        }

        for game_index in range(self.config.num_games):
            controller = self._create_controller(
                game_index
            )
            result = controller.run_game(
                max_turns=self.config.max_turns,
                verbose=False,
            )
            total_turns += result["total_turns"]
            if result["completed"]:
                completed_games += 1
                winner_name = result["winner"]
                winner_strategy = name_to_strategy[
                    winner_name
                ]
                wins[winner_strategy] += 1
            else:
                unfinished_games += 1
            # Record scores from all four players.
            for name, points in result["hand_points"].items():
                strategy = name_to_strategy[name]
                hand_points_total[strategy] += points
                player_appearances[strategy] += 1
            # Aggregate individual decision durations.
            for name, times in result[
                "decision_times_ms"
            ].items():
                strategy = name_to_strategy[name]
                decision_time_total[strategy] += sum(times)
                decision_count[strategy] += len(times)
            game_records.append({
                "game_number": game_index + 1,
                "completed": result["completed"],
                "winner": result["winner"],
                "winner_strategy": (
                    name_to_strategy[result["winner"]]
                    if result["winner"] is not None
                    else None
                ),
                "turns": result["total_turns"],
                "hand_points": dict(
                    result["hand_points"]
                ),
            })
            if verbose and (
                (game_index + 1) % 10 == 0
                or game_index + 1 == self.config.num_games
            ):
                print(
                    f"Completed {game_index + 1}/"
                    f"{self.config.num_games} simulations"
                )
        # Calculate final strategy-level statistics.
        strategy_results = {}
        for strategy in self.STRATEGIES:
            strategy_results[strategy] = {
                "wins": wins[strategy],
                "win_share_pct": (
                    100 * wins[strategy] / completed_games
                    if completed_games else 0.0
                ),
                "average_hand_points": (
                    hand_points_total[strategy]
                    / player_appearances[strategy]
                    if player_appearances[strategy]
                    else 0.0
                ),
                "average_decision_ms": (
                    decision_time_total[strategy]
                    / decision_count[strategy]
                    if decision_count[strategy]
                    else 0.0
                ),
                "decisions": decision_count[strategy],
                "appearances": player_appearances[strategy],
            }
        return {
            "total_games": self.config.num_games,
            "completed_games": completed_games,
            "unfinished_games": unfinished_games,
            "average_turns": (
                total_turns / self.config.num_games
            ),
            "strategies": strategy_results,
            "games": game_records,
        }


def print_experiment_results(results: dict) -> None:
    """Print a readable experiment summary."""
    print("\n" + "=" * 64)
    print("UNO AI - RANDOM VS GREEDY EXPERIMENT")
    print("=" * 64)
    print(f"Total games:     {results['total_games']}")
    print(f"Completed games: {results['completed_games']}")
    print(f"Unfinished:      {results['unfinished_games']}")
    print(
        f"Average turns:   "
        f"{results['average_turns']:.2f}"
    )
    print("\nStrategy Comparison")
    print("-" * 64)
    print(
        f"{'Metric':<27}"
        f"{'Random':>17}"
        f"{'Greedy':>17}"
    )
    print("-" * 64)
    strategies = results["strategies"]
    random_results = strategies["Random"]
    greedy_results = strategies["Greedy"]
    metrics = [
        ("Wins", "wins", ".0f"),
        ("Win share (%)", "win_share_pct", ".2f"),
        (
            "Avg remaining points",
            "average_hand_points",
            ".2f",
        ),
        (
            "Avg decision time (ms)",
            "average_decision_ms",
            ".5f",
        ),
        ("Total decisions", "decisions", ".0f"),
    ]
    for label, key, fmt in metrics:
        random_value = format(
            random_results[key], fmt
        )
        greedy_value = format(
            greedy_results[key], fmt
        )
        print(
            f"{label:<27}"
            f"{random_value:>17}"
            f"{greedy_value:>17}"
        )
    if results["completed_games"] == 0:
        print(
            "\nNo games finished. Win shares "
            "are undefined (displayed as 0)."
        )
    print("=" * 64)


def main():
    config = ExperimentConfig(
        num_games=40,
        max_turns=1000,
        base_seed=42,
    )
    experiment = AgentExperiment(config)
    results = experiment.run(verbose=True)
    print_experiment_results(results)


if __name__ == "__main__":
    main()

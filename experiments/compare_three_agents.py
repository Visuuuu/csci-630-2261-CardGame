from collections import defaultdict
from dataclasses import dataclass
from agents.greedy_agent import GreedyAgent
from agents.heuristic_agent import HeuristicAgent
from agents.random_agent import RandomAgent
from interface.game_controller import GameController


@dataclass(frozen=True)
class ThreeAgentConfig:
    num_games: int = 48
    max_turns: int = 1000
    base_seed: int = 42


class ThreeAgentExperiment:
    """Compare Random, Greedy, and Heuristic UNO agents."""
    STRATEGIES = ("Random", "Greedy", "Heuristic")
    def __init__(self, config: ThreeAgentConfig):
        if config.num_games <= 0:
            raise ValueError("num_games must be positive.")
        if config.num_games % 12 != 0:
            raise ValueError(
                "num_games must be a multiple of 12 "
                "for balanced seating."
            )
        if config.max_turns <= 0:
            raise ValueError("max_turns must be positive.")
        self.config = config

    def _get_lineup(self, game_index: int):
        """Rotate duplicate strategies and seating."""
        # Change duplicated strategy every four games.
        duplicate_index = (game_index // 4) % 3
        duplicate = self.STRATEGIES[duplicate_index]
        lineup = [
            ("Random 1", "Random"),
            ("Greedy 1", "Greedy"),
            ("Heuristic 1", "Heuristic"),
            (f"{duplicate} 2", duplicate),
        ]
        # Each four-game group visits every seat.
        shift = game_index % 4
        return (
            lineup[-shift:] + lineup[:-shift]
            if shift
            else lineup
        )

    def _create_controller(
        self,
        game_index: int,
    ) -> GameController:
        """Create a fresh match with four agents."""
        lineup = self._get_lineup(game_index)
        agents = []
        player_names = []
        for name, strategy in lineup:
            player_names.append(name)
            if strategy == "Random":
                # Separate seed for each random player.
                agent_number = int(name.split()[-1])
                seed = (
                    self.config.base_seed * 100_000
                    + game_index * 10
                    + agent_number
                )
                agent = RandomAgent(seed=seed)
            elif strategy == "Greedy":
                agent = GreedyAgent()
            else:
                agent = HeuristicAgent()
            agents.append(agent)
        return GameController(
            agents=agents,
            player_names=player_names,
            seed=self.config.base_seed + game_index,
        )

    def run(self, verbose: bool = True) -> dict:
        """Execute matches and aggregate strategy metrics."""
        wins = defaultdict(int)
        points_total = defaultdict(int)
        appearances = defaultdict(int)
        decision_time_total = defaultdict(float)
        decision_count = defaultdict(int)
        completed_games = 0
        unfinished_games = 0
        total_turns = 0
        game_records = []
        for game_index in range(self.config.num_games):
            lineup = self._get_lineup(game_index)
            strategy_by_name = {
                name: strategy
                for name, strategy in lineup
            }
            controller = self._create_controller(game_index)
            result = controller.run_game(
                max_turns=self.config.max_turns,
                verbose=False,
            )
            total_turns += result["total_turns"]
            winner_name = result["winner"]
            winner_strategy = None
            if result["completed"]:
                completed_games += 1
                winner_strategy = strategy_by_name[
                    winner_name
                ]
                wins[winner_strategy] += 1
            else:
                unfinished_games += 1
            for name, points in result["hand_points"].items():
                strategy = strategy_by_name[name]
                points_total[strategy] += points
                appearances[strategy] += 1
            for name, times in result[
                "decision_times_ms"
            ].items():
                strategy = strategy_by_name[name]
                decision_time_total[strategy] += sum(times)
                decision_count[strategy] += len(times)
            game_records.append({
                "game_number": game_index + 1,
                "lineup": list(lineup),
                "completed": result["completed"],
                "winner": winner_name,
                "winner_strategy": winner_strategy,
                "turns": result["total_turns"],
                "hand_points": dict(
                    result["hand_points"]
                ),
            })
            if verbose and (
                (game_index + 1) % 12 == 0
            ):
                print(
                    f"Completed {game_index + 1}/"
                    f"{self.config.num_games} games"
                )
        strategy_results = {}
        for strategy in self.STRATEGIES:
            strategy_results[strategy] = {
                "wins": wins[strategy],
                "win_share_pct": (
                    100 * wins[strategy] / completed_games
                    if completed_games else None
                ),
                "win_rate_per_appearance_pct": (
                    100 * wins[strategy] / appearances[strategy]
                    if appearances[strategy] else None
                ),
                "average_hand_points": (
                    points_total[strategy]
                    / appearances[strategy]
                    if appearances[strategy] else None
                ),
                "average_decision_ms": (
                    decision_time_total[strategy]
                    / decision_count[strategy]
                    if decision_count[strategy] else None
                ),
                "appearances": appearances[strategy],
                "decisions": decision_count[strategy],
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


def print_results(results: dict) -> None:
    """Display results for all three strategies."""
    print("\n" + "=" * 74)
    print("UNO AI - THREE STRATEGY COMPARISON")
    print("=" * 74)
    print(f"Total games: {results['total_games']}")
    print(f"Completed: {results['completed_games']}")
    print(f"Unfinished: {results['unfinished_games']}")
    print(f"Average turns: {results['average_turns']:.2f}")
    print("\nStrategy Results")
    print("-" * 74)
    def fmt(value, decimals=2):
        return (
            f"{value:.{decimals}f}"
            if value is not None
            else "N/A"
        )
    for name, stats in results["strategies"].items():
        print(f"\n{name}")
        print(f"  Wins: {stats['wins']}")
        print(
            "  Win share: "
            f"{fmt(stats['win_share_pct'])}%"
        )
        print(
            "  Wins per appearance: "
            f"{fmt(stats['win_rate_per_appearance_pct'])}%"
        )
        print(
            "  Avg remaining points: "
            f"{fmt(stats['average_hand_points'])}"
        )
        print(
            "  Avg decision time: "
            f"{fmt(stats['average_decision_ms'], 5)} ms"
        )
        print(f"  Decisions: {stats['decisions']}")
    print("=" * 74)


def main():
    config = ThreeAgentConfig(
        num_games=48,
        max_turns=1000,
        base_seed=42,
    )
    experiment = ThreeAgentExperiment(config)
    results = experiment.run(verbose=True)
    print_results(results)


if __name__ == "__main__":
    main()

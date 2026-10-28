from dataclasses import dataclass
from itertools import permutations
from agents.random_agent import RandomAgent
from agents.greedy_agent import GreedyAgent
from agents.heuristic_agent import HeuristicAgent
from agents.monte_carlo_agent import MonteCarloAgent
from interface.game_controller import GameController


@dataclass(frozen=True)
class FourAgentConfig:
    """Configuration for a four-strategy tournament."""
    num_games: int = 24
    max_turns: int = 1000
    base_seed: int = 42
    mc_simulations: int = 25
    mc_depth: int = 3
    include_draw_four: bool = False


class FourAgentExperiment:
    """Compare all four UNO AI strategies."""
    STRATEGIES = (
        "Random",
        "Greedy",
        "Heuristic",
        "Monte Carlo",
    )
    def __init__(self, config: FourAgentConfig):
        if config.num_games <= 0:
            raise ValueError("num_games must be positive.")
        if config.num_games % 24 != 0:
            raise ValueError(
                "num_games must be a multiple of 24."
            )
        if config.max_turns <= 0:
            raise ValueError("max_turns must be positive.")
        if config.mc_simulations <= 0:
            raise ValueError(
                "mc_simulations must be positive."
            )
        if config.mc_depth <= 0:
            raise ValueError(
                "mc_depth must be positive."
            )
        self.config = config
        # Every possible arrangement of four strategies.
        self.lineups = list(
            permutations(self.STRATEGIES)
        )

    def _get_lineup(self, game_index: int):
        """Get the seating order for one game."""
        return self.lineups[
            game_index % len(self.lineups)
        ]

    def _create_controller(
        self,
        game_index: int,
    ) -> GameController:
        """Create new agents and a fresh UNO game."""
        lineup = self._get_lineup(game_index)
        agents = []
        for strategy in lineup:
            if strategy == "Random":
                agent = RandomAgent(
                    seed=(
                        self.config.base_seed * 100_000
                        + game_index * 10
                        + 1
                    )
                )
            elif strategy == "Greedy":
                agent = GreedyAgent()
            elif strategy == "Heuristic":
                agent = HeuristicAgent()
            else:
                agent = MonteCarloAgent(
                    num_simulations=(
                        self.config.mc_simulations
                    ),
                    rollout_depth=self.config.mc_depth,
                    seed=(
                        self.config.base_seed * 100_000
                        + game_index * 10
                        + 4
                    ),
                    include_draw_four=self.config.include_draw_four,
                )
            agents.append(agent)
        return GameController(
            agents=agents,
            player_names=list(lineup),
            seed=self.config.base_seed + game_index,
            include_draw_four=(
                self.config.include_draw_four
            ),
        )


    def run(self, verbose: bool = True) -> dict:
        """Run matches and calculate performance metrics."""
        # Store aggregate measurements by strategy.
        statistics = {
            strategy: {
                "wins": 0,
                "hand_points_total": 0,
                "appearances": 0,
                "decision_time_total": 0.0,
                "decisions": 0,
            }
            for strategy in self.STRATEGIES
        }
        completed_games = 0
        unfinished_games = 0
        total_turns = 0
        game_records = []
        for game_index in range(
            self.config.num_games
        ):
            lineup = self._get_lineup(game_index)
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
                statistics[
                    result["winner"]
                ]["wins"] += 1
            else:
                unfinished_games += 1
            for strategy in self.STRATEGIES:
                stats = statistics[strategy]
                stats["appearances"] += 1
                stats["hand_points_total"] += (
                    result["hand_points"][strategy]
                )
                decision_times = result[
                    "decision_times_ms"
                ][strategy]
                stats["decision_time_total"] += sum(
                    decision_times
                )
                stats["decisions"] += len(
                    decision_times
                )
            game_records.append({
                "game_number": game_index + 1,
                "lineup": list(lineup),
                "completed": result["completed"],
                "winner": result["winner"],
                "turns": result["total_turns"],
                "hand_points": dict(
                    result["hand_points"]
                ),
            })
            if verbose and (
                (game_index + 1) % 6 == 0
                or game_index + 1 == self.config.num_games
            ):
                print(
                    f"Completed {game_index + 1}/"
                    f"{self.config.num_games} games"
                )
        strategy_results = {}
        for strategy, stats in statistics.items():
            appearances = stats["appearances"]
            decisions = stats["decisions"]
            strategy_results[strategy] = {
                "wins": stats["wins"],
                # Fraction of completed matches won.
                "win_share_pct": (
                    100 * stats["wins"] / completed_games
                    if completed_games > 0
                    else None
                ),
                # One appearance per strategy per game.
                "win_rate_per_appearance_pct": (
                    100 * stats["wins"] / appearances
                ),
                "average_hand_points": (
                    stats["hand_points_total"]
                    / appearances
                ),
                "average_decision_ms": (
                    stats["decision_time_total"]
                    / decisions
                    if decisions > 0
                    else None
                ),
                "appearances": appearances,
                "decisions": decisions,
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


def print_four_agent_results(results: dict):
    """Display the tournament results."""
    print("\n" + "=" * 72)
    print("UNO AI - FOUR-STRATEGY TOURNAMENT")
    print("=" * 72)
    print(f"Games: {results['total_games']}")
    print(f"Completed: {results['completed_games']}")
    print(f"Unfinished: {results['unfinished_games']}")
    print(
        f"Average turns: "
        f"{results['average_turns']:.2f}"
    )
    def display(value, digits=2):
        if value is None:
            return "N/A"
        return f"{value:.{digits}f}"
    for strategy, stats in results[
        "strategies"
    ].items():
        print("\n" + "-" * 72)
        print(strategy)
        print(f"  Wins: {stats['wins']}")
        print(
            "  Win share: "
            f"{display(stats['win_share_pct'])}%"
        )
        print(
            "  Win rate per appearance: "
            f"{display(stats['win_rate_per_appearance_pct'])}%"
        )
        print(
            "  Average remaining hand points: "
            f"{display(stats['average_hand_points'])}"
        )
        print(
            "  Average decision time: "
            f"{display(stats['average_decision_ms'], 5)} ms"
        )
        print(
            f"  Total decisions: {stats['decisions']}"
        )
    print("\n" + "=" * 72)


def main():
    config = FourAgentConfig(
        num_games=24,
        max_turns=1000,
        base_seed=42,
        mc_simulations=25,
        mc_depth=3,
    )
    experiment = FourAgentExperiment(config)
    results = experiment.run(verbose=True)
    print_four_agent_results(results)


if __name__ == "__main__":
    main()

from agents.greedy_agent import GreedyAgent
from agents.heuristic_agent import HeuristicAgent
from agents.monte_carlo_agent import MonteCarloAgent
from agents.random_agent import RandomAgent
from interface.game_controller import GameController


def create_four_agent_controller(
    game_seed: int = 42,
    monte_carlo_simulations: int = 50,
    monte_carlo_depth: int = 4,
) -> GameController:
    """Create a UNO game with four distinct AI agents."""
    player_names = [
        "Random",
        "Greedy",
        "Heuristic",
        "Monte Carlo",
    ]
    agents = [
        RandomAgent(seed=101),
        GreedyAgent(),
        HeuristicAgent(),
        MonteCarloAgent(
            num_simulations=monte_carlo_simulations,
            rollout_depth=monte_carlo_depth,
            seed=404,
        ),
    ]
    return GameController(
        agents=agents,
        player_names=player_names,
        seed=game_seed,
    )


def main():
    print("=" * 60)
    print("CSCI 630 - Comparative AI Agents")
    print("FOUR-PLAYER UNO AI DEMONSTRATION")
    print("=" * 60)
    controller = create_four_agent_controller()
    results = controller.run_game(
        max_turns=1000,
        verbose=True,
    )
    print("\n" + "=" * 60)
    print("AGENT PERFORMANCE SUMMARY")
    print("=" * 60)
    print(
        f"Game status: "
        f"{'Completed' if results['completed'] else 'Unfinished'}"
    )
    print(f"Winner: {results['winner'] or 'None'}")
    print(f"Total turns: {results['total_turns']}")
    print(
        f"\n{'Agent':<16}"
        f"{'Hand Points':>13}"
        f"{'Avg Time (ms)':>17}"
        f"{'Decisions':>12}"
    )
    print("-" * 60)
    for name in [
        "Random",
        "Greedy",
        "Heuristic",
        "Monte Carlo",
    ]:
        points = results["hand_points"][name]
        decision_times = results[
            "decision_times_ms"
        ][name]
        average_time = (
            sum(decision_times) / len(decision_times)
            if decision_times
            else 0.0
        )
        print(
            f"{name:<16}"
            f"{points:>13}"
            f"{average_time:>17.5f}"
            f"{len(decision_times):>12}"
        )
    print("\nFour-agent demonstration finished.")


if __name__ == "__main__":
    main()

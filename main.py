from agents.greedy_agent import GreedyAgent
from agents.random_agent import RandomAgent
from interface.game_controller import GameController


def main():
    print("CSCI 630 - Comparative AI Agents")
    print("UNO Strategic Card Game")
    player_names = [
        "Random Agent 1",
        "Greedy Agent 1",
        "Random Agent 2",
        "Greedy Agent 2",
    ]
    agents = [
        RandomAgent(seed=101),
        GreedyAgent(),
        RandomAgent(seed=202),
        GreedyAgent(),
    ]
    controller = GameController(
        agents=agents,
        player_names=player_names,
        seed=42,
    )
    results = controller.run_game(
        max_turns=1000,
        verbose=True,
    )
    print("\nAI Decision Time Summary")
    print("-" * 40)
    for name, times in results["decision_times_ms"].items():
        if times:
            average_time = sum(times) / len(times)
            print(
                f"{name}: "
                f"{average_time:.4f} ms "
                f"({len(times)} decisions)"
            )
    print("\nSimulation finished.")


if __name__ == "__main__":
    main()

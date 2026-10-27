from experiments.compare_four_agents import (
    FourAgentConfig,
    FourAgentExperiment,
    print_four_agent_results,
)
from experiments.four_agent_reporting import (
    FourAgentReporter,
)


def main():
    """Run the four-agent tournament and export results."""
    print("=" * 60)
    print("CSCI 630 - UNO AI Four-Agent Analysis")
    print("=" * 60)
    config = FourAgentConfig(
        num_games=24,
        max_turns=1000,
        base_seed=42,
        mc_simulations=25,
        mc_depth=3,
    )
    experiment = FourAgentExperiment(config)
    print("\nRunning the four-agent tournament...")
    results = experiment.run(verbose=True)
    print_four_agent_results(results)
    reporter = FourAgentReporter(
        output_dir="reports/four_agents"
    )
    reporter.generate_report(results)
    print("\nReport generation completed!")


if __name__ == "__main__":
    main()

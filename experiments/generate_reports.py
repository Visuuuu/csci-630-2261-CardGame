from experiments.compare_agents import (
    AgentExperiment,
    ExperimentConfig,
    print_experiment_results,
)
from experiments.reporting import ExperimentReporter


def main():
    """Run experiments and generate output files."""
    print("=" * 55)
    print("CSCI 630 - UNO AI Experimental Analysis")
    print("=" * 55)
    config = ExperimentConfig(
        num_games=40,
        max_turns=1000,
        base_seed=42,
    )
    experiment = AgentExperiment(config)
    print("\nRunning UNO simulations...")
    results = experiment.run(verbose=True)
    # Print the same terminal summary as Step 14.
    print_experiment_results(results)
    # Export the actual experimental results.
    reporter = ExperimentReporter(
        output_dir="reports"
    )
    reporter.generate_report(results)
    print("\nAnalysis completed successfully!")


if __name__ == "__main__":
    main()

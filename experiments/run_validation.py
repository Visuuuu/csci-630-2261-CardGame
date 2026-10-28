from pathlib import Path
from experiments.compare_four_agents import (
    FourAgentConfig,
    FourAgentExperiment,
    print_four_agent_results,
)
from experiments.statistical_analysis import (
    analyze_tournament,
    export_statistical_summary,
)


OUTPUT_DIR = Path("reports/validation")


def run_scenario(
    name: str,
    include_draw_four: bool,
    num_games: int = 24,
    base_seed: int = 42,
    mc_simulations: int = 25,
    mc_depth: int = 3,
) -> list[dict]:
    """Run one ruleset scenario and export its statistics."""
    config = FourAgentConfig(
        num_games=num_games,
        max_turns=1000,
        base_seed=base_seed,
        mc_simulations=mc_simulations,
        mc_depth=mc_depth,
        include_draw_four=include_draw_four,
    )
    print(f"\n{'=' * 60}")
    print(f"Experiment: {name}")
    print(f"Games: {num_games}")
    print(f"Wild Draw Four: {include_draw_four}")
    print(f"{'=' * 60}")
    experiment = FourAgentExperiment(config)
    results = experiment.run(verbose=True)
    print_four_agent_results(results)
    rows = analyze_tournament(
        results=results,
        ruleset=name,
        mc_simulations=mc_simulations,
        mc_depth=mc_depth,
    )
    output_path = OUTPUT_DIR / (
        f"{name}_statistical_summary.csv"
    )
    export_statistical_summary(
        rows,
        output_path,
    )
    print(f"\nSaved: {output_path.resolve()}")
    return rows


def main():
    # Run independent analyses of the two rulesets.
    baseline_rows = run_scenario(
        name="baseline_104",
        include_draw_four=False,
    )
    extended_rows = run_scenario(
        name="extended_108",
        include_draw_four=True,
    )
    combined_rows = baseline_rows + extended_rows
    export_statistical_summary(
        combined_rows,
        OUTPUT_DIR / "combined_statistical_summary.csv",
    )
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    for row in combined_rows:
        print(
            f"{row['ruleset']:<15}"
            f"{row['strategy']:<15}"
            f"Win rate: {row['win_rate_pct']:>6.2f}%  "
            f"95% CI: "
            f"[{row['ci_lower_pct']:.2f}%, "
            f"{row['ci_upper_pct']:.2f}%]"
        )
    print("\nValidation reports generated.")


if __name__ == "__main__":
    main()

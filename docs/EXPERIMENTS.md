
# Experimental Methodology and Reproducibility

## 1. Research Questions

The project addresses:

- RQ1: How do Random, Greedy, Heuristic and
  Monte Carlo agents compare in a four-player
  UNO-style card game?
- RQ2: How does adding Wild Draw Four affect
  observed performance?
- RQ3: How does Monte Carlo simulation budget
  affect win rate, remaining points and decision time?
- RQ4: How does legal opponent-transition sampling
  affect Monte Carlo V2 relative to V1?

## 2. Main Evaluation Metrics

### Win Rate

Win rate is calculated as:

```text
Win rate (%) = 100 * wins / appearances
```

All appearances are included in the denominator,
including games that reach the turn limit without
producing a winner.

### Average Remaining Hand Points

The mean point total remaining in an agent's hand
at the end of a completed or capped match.

Lower values are preferable.

### Average Decision Time

The mean elapsed time required for an agent
to select an action, measured in milliseconds.

Lower values indicate faster action selection.

Time measurements depend on the testing computer
and runtime conditions.

## 3. Four-Agent Tournament

Primary agents:

- Random
- Greedy
- Heuristic
- Monte Carlo V1

The tournament rotates seating arrangements to reduce
the influence of starting position.

The standard comparison uses all 24 permutations of
the four strategies.

## 4. Ruleset Validation

Two settings are evaluated separately:

| Setting | Deck | Wild Draw Four |
|---|---:|---|
| Baseline | 104 cards | Disabled |
| Extended | 108 cards | Enabled |

The validation runs 24 tournament games per ruleset
in the initial study.

Results are written to:

```text
reports/validation/
```

Run:

```bash
python -m experiments.run_validation
```

## 5. Monte Carlo Simulation Budget Study

Monte Carlo V1 is evaluated with:

- 25 simulations per candidate
- 50 simulations per candidate
- 100 simulations per candidate

The initial study uses 24 games for each budget,
72 games in total.

Other agents and settings remain consistent.

Run:

```bash
python -m experiments.monte_carlo_budget
python -m experiments.plot_monte_carlo_budget
```

Main results:

```text
reports/monte_carlo_budget/budget_summary.csv
reports/monte_carlo_budget/budget_games.csv
reports/monte_carlo_budget/charts/
```

Increasing the simulation budget may improve action
evaluation but increases computational cost.

More simulations do not automatically correct
an inaccurate rollout model.

## 6. Monte Carlo V1 vs. V2

V1 and V2 are evaluated in separate four-agent
tournaments against Random, Greedy and Heuristic.

Each version uses:

- 24 matches
- Identical seating permutations
- Matching initial deck seeds
- 25 simulations per candidate
- Rollout depth of 3
- 104-card baseline ruleset

Run:

```bash
python -m experiments.compare_monte_carlo_versions
python -m experiments.plot_monte_carlo_versions
```

Main results:

```text
reports/monte_carlo_versions/version_summary.csv
reports/monte_carlo_versions/paired_games.csv
reports/monte_carlo_versions/charts/
```

Matching initial seeds does not mean that the
subsequent simulated matches are identical.

Agent decisions change gameplay, causing trajectories
to diverge.

Matched-game outcomes count:

- Both versions win their respective matches
- V1 wins but V2 loses
- V2 wins but V1 loses
- Neither version wins

## 7. Statistical Interpretation

Wilson 95% confidence intervals are calculated for
individual observed win rates.

Small samples, shared initial conditions and the
four-player competition structure limit inference.

The intervals should not be interpreted as direct
significance tests of performance differences.

Observed rankings are descriptive. Stronger claims
would require more independent games and an analysis
suited to the experimental dependence structure.

## 8. Reproduce the Results

From the project root:

```bash
python -m unittest discover -s tests -p "test_*.py" -v

python -m experiments.run_validation

python -m experiments.monte_carlo_budget
python -m experiments.plot_monte_carlo_budget

python -m experiments.compare_monte_carlo_versions
python -m experiments.plot_monte_carlo_versions

python -m experiments.final_analysis

python -m experiments.system_check
```

The completed initial experiments use fixed random
seeds to support reproducibility.

Timing results can vary even when game decisions
are reproducible.

## 9. Consolidated Research Summary

After generating the experiment reports:

```bash
python -m experiments.final_analysis
```

This produces:

```text
reports/final_analysis/final_research_summary.md
reports/final_analysis/final_research_data.json
```

The final summary contains measured tournament values.

The summary should be reviewed before making claims
about which strategy or configuration performed best.

## 10. Limitations

- Simplified UNO rules
- Four players rather than arbitrary player counts
- No human-player strategy evaluation
- Limited tournament sample sizes
- No complete hidden-information game-tree search
- Monte Carlo V1 uses approximate hypothetical futures
- Monte Carlo V2 samples legal opponent moves but
  does not retain full persistent opponent state
- Decision times are hardware-dependent
- The game is stochastic, so individual match
  outcomes are not reliable measures of superiority

## 11. Future Work

Possible improvements beyond the current project:

- Larger, repeated tournaments using additional seeds
- Confidence intervals for paired performance differences
- More realistic full-game Monte Carlo rollouts
- Opponent-hand-size modeling using public information
- Additional heuristics and ablation experiments
- Human-versus-AI gameplay
- Automated figure generation for presentation slides

These are future directions, not implemented features.

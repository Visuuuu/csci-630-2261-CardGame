# Comparative AI Agents for a Strategic Card Game

## Final Experimental Results and Analysis

Generated from the project's existing CSV reports.

### 1. Four-agent comparison by ruleset

#### baseline_104

| Strategy | Wins | Win rate (%) | CI low (%) | CI high (%) | Avg hand points | Avg decision (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| Random | 4 | 16.67 | 6.68 | 35.85 | 28.83 | 0.00 |
| Greedy | 8 | 33.33 | 17.97 | 53.29 | 17.17 | 0.00 |
| Heuristic | 4 | 16.67 | 6.68 | 35.85 | 10.38 | 0.00 |
| Monte Carlo | 8 | 33.33 | 17.97 | 53.29 | 16.62 | 1.58 |

#### extended_108

| Strategy | Wins | Win rate (%) | CI low (%) | CI high (%) | Avg hand points | Avg decision (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| Random | 7 | 29.17 | 14.91 | 49.17 | 25.38 | 0.00 |
| Greedy | 8 | 33.33 | 17.97 | 53.29 | 26.29 | 0.00 |
| Heuristic | 4 | 16.67 | 6.68 | 35.85 | 22.08 | 0.00 |
| Monte Carlo | 5 | 20.83 | 9.24 | 40.47 | 29.58 | 1.75 |

Results from the two rulesets are shown separately because the legal card set differs.

### 2. Monte Carlo simulation budget

| Simulations | Wins | Win rate (%) | Avg points | Avg decision (ms) |
| --- | --- | --- | --- | --- |
| 25 | 8 | 33.33 | 16.62 | 1.62 |
| 50 | 8 | 33.33 | 16.58 | 3.08 |
| 100 | 11 | 45.83 | 15.12 | 5.91 |

Highest observed win-rate budget: **100**.

Lowest observed decision-time budget: **25**.

These are descriptive rankings, not proof that a particular simulation budget is optimal.

### 3. Monte Carlo V1 versus V2

| Version | Wins | Win rate (%) | CI low (%) | CI high (%) | Avg points | Avg decision (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| V1 | 8 | 33.33 | 17.97 | 53.29 | 16.62 | 1.64 |
| V2 | 9 | 37.50 | 21.16 | 57.29 | 19.38 | 2.36 |

Observed V2 minus V1 differences:

- Win rate: +4.17 percentage points.
- Average remaining hand points: +2.75.
- Average decision time: +0.7215 ms.

#### Matched initial conditions

- Both versions won: 5
- Only V1 won: 3
- Only V2 won: 4
- Neither version won: 12
- Total matched pairs: 24

A negative remaining-points difference favors V2, while a positive decision-time difference means V2 required more computation.

### 4. Interpretation and limitations

1. The four primary AI strategies were Random, Greedy, Heuristic and Monte Carlo.
2. Win rate, remaining hand points and decision time are different performance dimensions; none alone establishes overall algorithm superiority.
3. The win-rate intervals are Wilson 95% intervals for individual observed rates. They are not confidence intervals for the difference between two strategies.
4. Matches using shared starting seeds can diverge after different agent decisions. Matched seeds control initial conditions, not entire trajectories.
5. Monte Carlo V1 uses approximate futures. V2 samples legal hypothetical opponent moves but does not model persistent full four-player hidden hands or all action-card effects.
6. Observed decision times depend on the computer and runtime conditions.
7. Small tournament samples limit the strength of statistical conclusions. Further independent tournament blocks would strengthen future research.

### 5. Supporting figures

- `reports/monte_carlo_budget/charts/`
- `reports/monte_carlo_versions/charts/`

The figures and tables should be reviewed together when preparing the final presentation.

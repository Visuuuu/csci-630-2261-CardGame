
# Comparative AI Agents for a Strategic Card Game

**Course:** CSCI 630  
**Project:** Comparative AI Agents for a Strategic Card Game  
**Game:** Four-player UNO-style strategic card game  
**Repository:** https://github.com/Visuuuu/csci-630-2261-CardGame

## Overview

This project implements a four-player UNO-style card game
in Python to compare several artificial intelligence
decision-making strategies under controlled conditions.

The four primary strategies are:

1. Random Agent
2. Greedy Agent
3. Heuristic / Rule-Based Agent
4. Monte Carlo Agent

An additional Monte Carlo V2 implementation investigates
whether sampling legal hypothetical opponent moves changes
performance compared with the original Monte Carlo model.

The project provides:

- A modular UNO-style game engine
- Configurable AI-controlled players
- A Tkinter graphical interface for live demonstrations
- Automated tournament experiments
- CSV performance reports
- Matplotlib comparison charts
- Statistical analysis and integration tests

Game data is generated through simulations; no external
training dataset is required.

## Research Objectives

The project evaluates:

1. How different AI decision strategies affect win rate.
2. How strategies affect average remaining hand points.
3. How much computation time each strategy requires.
4. Whether increasing Monte Carlo simulation budget
   improves performance.
5. Whether the V2 rollout model changes Monte Carlo
   performance relative to the original version.

## Technologies

- Python 3.10 or newer
- Python standard library
- Tkinter for the graphical interface
- Matplotlib for experiment charts
- unittest for automated testing

No machine-learning training framework is required.
The AI agents use rule-based decisions and simulation,
not models trained on labeled data.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Visuuuu/csci-630-2261-CardGame.git
cd csci-630-2261-CardGame
```

### 2. Create a virtual environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install matplotlib
```

Tkinter is included with many Python installations.
Some Linux distributions require a separate Tkinter package.

You can check Tkinter with:

```bash
python -m tkinter
```

### 4. Run the GUI

From the repository root:

```bash
python -m interface.uno_gui
```

The graphical interface allows the user to:

- Assign AI strategies to four player positions
- Select Monte Carlo V1 or V2
- Apply a V1-versus-V2 demonstration preset
- Enable or disable Wild Draw Four
- Start new games
- Advance one turn at a time
- Automatically play and pause games
- Display decision statistics
- Optionally reveal hands to the audience

The audience hand-reveal option affects the display.
AI agents continue receiving restricted observations.

## Game Rules

The default game uses a simplified 104-card UNO-style deck.

It includes number cards, Skip, Reverse, Draw Two, and Wild.
Wild Draw Four is excluded from the default mode.

An optional 108-card mode adds four Wild Draw Four cards.

Key simplifications include:

- Four AI-controlled players
- Seven starting cards per player
- Normal color, number, and action matching
- A single draw and pass when no legal card is available
- No stacking
- No jump-ins
- No manual UNO calls or calling penalties
- Automatic "UNO!" notification at one remaining card
- Immediate victory when a player plays their final card

Wild Draw Four in extended mode is playable only when
the player holds no other card matching the active color.
There is no Wild Draw Four challenge system.

These are project-specific game rules, not a claim to
implement every official UNO rule.

## AI Strategies

| Agent | Decision approach |
|---|---|
| Random | Random legal action |
| Greedy | Prioritizes discarding high-value cards |
| Heuristic | Scores cards using hand composition, action benefits and endgame factors |
| Monte Carlo V1 | Evaluates actions using randomized approximate future play |
| Monte Carlo V2 | Extends V1 by sampling hypothetical legal opponent moves |

Monte Carlo V2 is a supplementary research comparison.
The original four-agent study remains the primary scope.

Neither Monte Carlo implementation is a full
hidden-information, four-player game simulator.

## Running Experiments

Run the original four-agent tournament:

```bash
python -m experiments.compare_four_agents
```

Generate the four-agent reports:

```bash
python -m experiments.generate_four_agent_reports
```

Run baseline and extended-ruleset validation:

```bash
python -m experiments.run_validation
```

Compare Monte Carlo simulation budgets:

```bash
python -m experiments.monte_carlo_budget
```

Generate Monte Carlo budget charts:

```bash
python -m experiments.plot_monte_carlo_budget
```

Compare Monte Carlo V1 with V2:

```bash
python -m experiments.compare_monte_carlo_versions
```

Generate V1/V2 comparison charts:

```bash
python -m experiments.plot_monte_carlo_versions
```

Consolidate the experimental findings:

```bash
python -m experiments.final_analysis
```

Run the final system integration check:

```bash
python -m experiments.system_check
```

Tournament output files and figures are generated
under the `reports/` directory.

## Evaluation Metrics

The main performance measures are:

- **Win rate:** Wins divided by agent appearances
- **Average remaining hand points:** Mean hand score
  remaining at the end of each game
- **Average decision time:** Mean time spent selecting
  an action, measured in milliseconds

Win-rate reports include Wilson 95% confidence intervals
for individual observed rates.

These intervals do not, by themselves, demonstrate a
statistically significant difference between agents.

## Testing

Run the complete automated test suite:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

The project includes tests for:

- Cards, decks, and game rules
- AI agents and legal decisions
- Four-player game execution
- Optional Wild Draw Four behavior
- Experiment aggregation and statistical analysis
- CSV reports and comparison charts
- GUI configuration and asynchronous turns
- System integration

The 255 tests confirmed through Step 34 passed before
this documentation update.

## Project Organization

```text
agents/       AI decision-making strategies
uno_game/     Cards, deck, rules, players and game engine
interface/    Controller, Tkinter GUI and demonstration logic
experiments/  Tournaments, statistics, reports and charts
tests/        Automated test suite
reports/      Generated experiment outputs (locally ignored)
docs/         Architecture and experiment documentation
```

## Experimental Limitations

- The game uses simplified UNO rules.
- The Monte Carlo rollout models are approximate.
- Opponents' hidden cards are not provided to agents.
- Monte Carlo V2 uses sampled, not actual, opponent hands.
- Simulation trajectories may diverge despite shared seeds.
- Pilot tournaments contain relatively few games.
- Decision times depend on hardware and system load.
- Performance differences should not be described
  as statistically conclusive without further testing.

## Additional Documentation

- [Architecture and Rules](docs/ARCHITECTURE.md)
- [Experimental Methodology](docs/EXPERIMENTS.md)

## Repository

https://github.com/Visuuuu/csci-630-2261-CardGame

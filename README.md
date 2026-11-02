# Comparative AI Agents for a Strategic Card Game

**Course:** CSCI 630  
**Project:** Comparative AI Agents for a Strategic Card Game  
**Game:** Four-player UNO-style strategic card game  
**Repository:** https://github.com/Visuuuu/csci-630-2261-CardGame

## Overview

This project is a four-player UNO-style card game built in Python to compare different AI decision-making strategies. All agents play using the same game rules, so their performance can be measured under consistent conditions.

The four main strategies are Random, Greedy, Heuristic (Rule-Based), and Monte Carlo. The project also includes Monte Carlo V2, an additional version that samples hypothetical legal opponent moves during simulations.

The project includes:

- A separate UNO game engine and AI agent implementations
- A Tkinter interface for watching AI matches and playing against the agents
- Local games with any combination of human and AI players
- Automated tournaments and performance comparisons
- CSV reports, Matplotlib charts, and statistical analysis
- Unit and integration tests

The experiments generate their own game data. No external training dataset or model training is required.

## Research Objectives

The main research questions are:

1. How do different AI strategies compare in win rate?
2. How do they compare in average remaining hand points?
3. How much time does each strategy take to choose a move?
4. Does increasing the Monte Carlo simulation budget improve performance?
5. How does Monte Carlo V2 compare with the original Monte Carlo agent?

Human-player games are an extra feature and are not included in the automated AI comparisons.

## Technologies

- Python 3.10 or newer
- Tkinter for the desktop interface
- Matplotlib for charts
- Python `unittest` for testing

The AI strategies use rules and simulations rather than a trained machine-learning model.

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
python -m pip install -r requirements.txt
```

Tkinter is included with many Python installations, although some Linux distributions require it to be installed separately. You can check whether it is available with:

```bash
python -m tkinter
```

### 4. Run the game

From the project root:

```bash
python -m interface.uno_gui
```

In the GUI, you can start a new game, choose the players, enable the optional Wild Draw Four ruleset, advance turns manually, or use Auto Play for AI turns. The interface also displays the action history and AI decision statistics.

For AI-only demonstrations, you can select a Monte Carlo V1 versus V2 preset and optionally reveal all hands. Revealing hands changes only the display; AI agents still receive restricted observations.

## Human Player Mode

Each of the four player positions can be assigned to a human or an AI strategy. This allows one human to play against three AI agents, a mix of human and AI players, or four people to play on the same computer.

Human players select cards by clicking them in the interface. Only legal cards are enabled. Playing a Wild card opens a color-selection window, and the Draw Card button becomes available when there is no legal move.

For local multiplayer, each human player's hand stays hidden until they click **Reveal My Hand** at the start of their turn. The computer can then be passed to the next person without immediately showing their cards. **Reveal All Hands (Demo)** is disabled when a game includes human players.

This is shared-computer multiplayer, not online multiplayer across separate devices.

## Game Rules

The default game uses a simplified 104-card UNO-style deck with number cards, Skip, Reverse, Draw Two, and Wild cards. An optional 108-card ruleset adds four Wild Draw Four cards.

The game follows these rules:

- Four players, controlled by humans or AI agents
- Seven starting cards for each player
- Matching by color, number, or action type
- Skip, Reverse, Draw Two, and Wild card effects
- Draw one card and pass if no legal card is available
- Automatic "UNO!" notification when a player has one card left
- Immediate victory when a player plays their final card

Stacking, jump-ins, manual UNO calling penalties, and Wild Draw Four challenges are not implemented.

In the extended ruleset, a Wild Draw Four can be played only when the player has no card matching the active color. The following player draws four cards and loses a turn.

These are the rules used by this project, not a full implementation of every official UNO rule.

## AI Strategies

| Agent | Decision approach |
|---|---|
| Random | Chooses randomly from legal moves |
| Greedy | Prioritizes discarding higher-value cards |
| Heuristic / Rule-Based | Scores moves using hand composition, action cards, and endgame considerations |
| Monte Carlo V1 | Estimates move quality through approximate future simulations |
| Monte Carlo V2 | Extends V1 by sampling hypothetical legal opponent moves |

The primary experiment compares Random, Greedy, Heuristic, and Monte Carlo V1. Monte Carlo V2 is a supplementary comparison.

Neither Monte Carlo version performs complete four-player hidden-information game simulations. The agents do not receive opponents' actual cards, even when the GUI is set to reveal hands for a demonstration.

## Running Experiments

Run these commands from the project root.

**Four-agent tournament:**

```bash
python -m experiments.compare_four_agents
```

**Four-agent reports:**

```bash
python -m experiments.generate_four_agent_reports
```

**Baseline and extended-ruleset validation:**

```bash
python -m experiments.run_validation
```

**Monte Carlo simulation budget comparison and charts:**

```bash
python -m experiments.monte_carlo_budget
python -m experiments.plot_monte_carlo_budget
```

**Monte Carlo V1 versus V2 comparison and charts:**

```bash
python -m experiments.compare_monte_carlo_versions
python -m experiments.plot_monte_carlo_versions
```

**Consolidated research analysis:**

```bash
python -m experiments.final_analysis
```

**System integration check:**

```bash
python -m experiments.system_check
```

Experiment results and figures are written to the `reports/` directory. The reporting scripts can regenerate these files.

## Evaluation Metrics

The experiments compare agents using:

- **Win rate:** Wins divided by the number of games in which an agent participates
- **Average remaining hand points:** Average card-point total left in a player's hand at the end of a game
- **Average decision time:** Average time an AI agent takes to choose a move, in milliseconds

Win-rate reports also include Wilson 95% confidence intervals. These intervals describe uncertainty in individual observed win rates; they do not by themselves prove that one agent significantly outperforms another.

## Testing

Run the complete automated test suite:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

The tests cover game rules, cards and decks, AI decisions, Wild Draw Four behavior, experimental calculations, report generation, GUI configuration, asynchronous AI turns, and human-player controller behavior.

Human gameplay should also be checked manually in the Tkinter interface, especially card selection, Wild color selection, turn handoffs, and games with multiple human players.

## Project Organization

```text
agents/       AI strategies and human-player representation
uno_game/     Cards, deck, players, game rules, and game engine
interface/    Controller, Tkinter GUI, and demonstration logic
experiments/  Tournaments, statistics, reporting, and charts
tests/        Automated tests
reports/      Generated experimental results and figures
docs/         Architecture and experiment documentation
```

## Limitations

- The game uses a simplified version of UNO rules.
- Both Monte Carlo agents use approximate simulations.
- Monte Carlo V2 samples hypothetical opponent cards rather than actual hidden hands.
- Tournament sample sizes are relatively small, so performance differences should be interpreted cautiously.
- Measured decision times can vary by computer and system load.
- Human multiplayer currently runs locally on one shared computer; it does not support separate devices or online rooms.

## Additional Documentation

- [Architecture and Game Rules](docs/ARCHITECTURE.md)
- [Experimental Methodology](docs/EXPERIMENTS.md)

## Repository

https://github.com/Visuuuu/csci-630-2261-CardGame

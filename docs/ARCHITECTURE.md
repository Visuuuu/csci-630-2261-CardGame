
# System Architecture and Game Rules

## 1. Design Goals

The application separates game logic from AI strategies,
the graphical interface, and experimental evaluation.

This design supports comparing algorithms without
rewriting the core game.

## 2. Architecture

```text
                  +----------------------+
                  | Tkinter GUI / Demo   |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | GameController       |
                  | Turn execution       |
                  | Timing and records   |
                  +----------+-----------+
                             |
             +---------------+----------------+
             |                                |
             v                                v
  +----------------------+        +----------------------+
  | UNO Game Engine      |        | AI Agent             |
  | Deck / Cards         |        | Random / Greedy      |
  | Legal Moves / Turns  |        | Heuristic / MC V1/V2 |
  +----------------------+        +----------------------+
                                             ^
                                             |
                                  AgentObservation
                                  Public state and
                                  own hand only
```

Experiments create game controllers, run matches,
aggregate performance metrics, and write reports.

## 3. Module Responsibilities

### `uno_game/`

Contains the rules and game state.

Main modules:

- `card.py`: Card types, colors and point values
- `deck.py`: Deck generation, shuffling and drawing
- `player.py`: Player hand management
- `rules.py`: Legal card matching
- `game.py`: Turn progression, special cards and victory

The engine does not depend on how an AI selects moves.

### `agents/`

Contains decision-making strategies.

- `random_agent.py`
- `greedy_agent.py`
- `heuristic_agent.py`
- `monte_carlo_agent.py`
- `monte_carlo_v2_agent.py`
- `base_agent.py`

All strategies operate through the agent observation
and decision interface.

### `interface/`

Connects the game and agents.

- `game_controller.py`: Executes turns and records timing
- `demo_config.py`: Creates configurable player lineups
- `game_view.py`: Prepares display information
- `uno_gui.py`: Tkinter live demonstration
- `async_turn.py`: Runs AI computation off the GUI thread

The GUI uses an asynchronous decision runner to avoid
blocking user-interface updates during slower AI moves.

### `experiments/`

Contains controlled tournament and analysis scripts.

Experiment code remains separate from the game engine.

### `tests/`

Contains automated unit, integration, reporting,
and configuration tests.

## 4. Information Restrictions

An AI observes:

1. Its own hand
2. Legal cards from that hand
3. The visible top discard
4. The active color

The agent does not receive the actual opponent hands,
draw pile, or private game state through its observation.

Monte Carlo agents construct hypothetical card samples
from a reference deck rather than inspecting real hidden
cards.

Audience reveal mode is a display feature and does
not expand the agent observation.

## 5. UNO Rulesets

### Baseline: 104 cards

Standard colored number and action cards, plus ordinary
Wild cards, without Wild Draw Four.

### Extended: 108 cards

Adds four Wild Draw Four cards.

A Wild Draw Four is legal only if the player holds
no other card matching the current active color.

Playing it changes the active color and causes the next
player to draw four and lose a turn.

### Simplified Rules

- Seven cards are dealt to each of four players.
- Normal matching uses color, number or action type.
- Wild cards require a color selection.
- Skip and Reverse affect turn progression.
- Draw Two causes a two-card draw and skipped turn.
- A player with no legal move draws one and passes.
- Stacking and jump-ins are disabled.
- Calling penalties are not used.
- The interface announces UNO automatically.
- Playing the final card ends the game immediately.
- There is no Wild Draw Four challenge mechanic.

These rules are deliberately limited to maintain
a consistent AI evaluation environment.

## 6. AI Strategies

### Random

Selects a legal action using a seeded random generator.

### Greedy

Prioritizes discarding the highest-point legal card.
For Wild cards, it selects a color based on the
remaining hand.

### Heuristic / Rule-Based

Scores candidate moves using card points, same-color
hand composition, action-card bonuses, Wild
preservation, and endgame adjustments.

### Monte Carlo V1

Evaluates candidate actions using several randomized,
limited-horizon approximate continuations.

The reward emphasizes shedding cards and reducing
remaining points.

### Monte Carlo V2

Reuses the original action evaluation framework but
samples a hypothetical opponent hand to check legal
opponent plays during rollouts.

This is not a complete information-set search or
full four-player simulator.

## 7. Turn Execution

1. Controller identifies the active player.
2. Controller constructs the restricted observation.
3. Agent selects a legal action and optional Wild color.
4. Engine validates and applies the action.
5. Controller records the turn and decision time.
6. GUI refreshes the visible state.
7. Repeat until victory or the configured turn limit.

## 8. Design Trade-offs

The modular architecture improves testability and
comparability.

Monte Carlo approximations keep computation practical,
but they limit how realistically future gameplay
is represented.

The live GUI is designed for demonstrations. Automated
tournaments provide the primary evidence for comparing
agent performance.

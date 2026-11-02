from dataclasses import dataclass
from time import perf_counter
from agents.base_agent import (
    AgentDecision,
    AgentObservation,
    BaseAgent,
)
from uno_game.game import UNOGame
from agents.human_player import HumanPlayer


@dataclass(frozen=True)
class TurnRecord:
    """Public details of an executed turn."""
    turn_number: int
    player_id: int
    player_name: str
    message: str
    decision_time_ms: float


class GameController:
    """Connect AI agents to the UNO game engine."""
    def __init__(
        self,
        agents: list[BaseAgent | HumanPlayer],
        player_names: list[str],
        seed: int | None = None,
        include_draw_four: bool = False,
    ):
        if len(agents) != UNOGame.NUM_PLAYERS:
            raise ValueError(
                "Exactly four players are required."
            )
        if not all(
                isinstance(agent, (BaseAgent, HumanPlayer))
                for agent in agents
        ):
            raise TypeError(
                "Each player must be an AI agent or HumanPlayer."
            )
        self.agents = list(agents)
        self.game = UNOGame(
            player_names=player_names,
            seed=seed,
            include_draw_four=include_draw_four,
        )
        self.turn_history: list[TurnRecord] = []

    @property
    def is_human_turn(self) -> bool:
        """Whether the current player needs human input."""
        if self.game.game_over:
            return False
        player_id = self.game.current_player.player_id
        return isinstance(
            self.agents[player_id],
            HumanPlayer,
        )

    def _create_observation(self) -> AgentObservation:
        """Create a restricted current-player observation."""
        player = self.game.current_player
        return AgentObservation(
            hand=player.hand,
            legal_cards=tuple(
                self.game.get_current_legal_cards()
            ),
            top_card=self.game.top_card,
            active_color=self.game.active_color,
        )

    def step(self) -> TurnRecord:
        """Request and execute one AI decision."""
        if self.game.game_over:
            raise ValueError(
                "Cannot take a turn after the game ends."
            )
        if self.is_human_turn:
            raise ValueError(
                "This is a human turn. "
                "Use submit_human_turn() instead."
            )
        player = self.game.current_player
        player_id = player.player_id
        agent = self.agents[player_id]
        observation = self._create_observation()
        start = perf_counter()
        decision = agent.choose_action(observation)
        elapsed_ms = (
            perf_counter() - start
        ) * 1000
        if not isinstance(decision, AgentDecision):
            raise TypeError(
                "Agent must return an AgentDecision."
            )
        # The engine is responsible for move validation.
        message = self.game.play_turn(
            card=decision.card,
            chosen_color=decision.chosen_color,
        )
        record = TurnRecord(
            turn_number=self.game.turn_count,
            player_id=player_id,
            player_name=player.name,
            message=message,
            decision_time_ms=elapsed_ms,
        )
        self.turn_history.append(record)
        return record

    def submit_human_turn(
        self,
        card=None,
        chosen_color=None,
    ) -> TurnRecord:
        """Apply a move selected by the human player."""
        if self.game.game_over:
            raise ValueError(
                "Cannot take a turn after the game ends."
            )
        if not self.is_human_turn:
            raise ValueError(
                "The current player is controlled by AI."
            )
        player = self.game.current_player
        player_id = player.player_id
        # The engine validates the selected card.
        message = self.game.play_turn(
            card=card,
            chosen_color=chosen_color,
        )
        record = TurnRecord(
            turn_number=self.game.turn_count,
            player_id=player_id,
            player_name=player.name,
            message=message,
            decision_time_ms=0.0,
        )
        self.turn_history.append(record)
        return record

    def run_game(
        self,
        max_turns: int = 1000,
        verbose: bool = True,
    ) -> dict:
        """Run a match until victory or the turn limit."""
        if max_turns <= 0:
            raise ValueError(
                "max_turns must be greater than zero."
            )
        if any(
                isinstance(agent, HumanPlayer)
                for agent in self.agents
        ):
            raise ValueError(
                "run_game() supports AI-only matches. "
                "Human games must be played interactively."
            )
        if verbose:
            print("\n" + "=" * 55)
            print("UNO AI - Automated Four-Player Match")
            print("=" * 55)
            for player in self.game.players:
                print(
                    f"Player {player.player_id}: "
                    f"{player.name}"
                )
            print(f"\nStarting card: {self.game.top_card}")
            print(f"Active color: {self.game.active_color.value}")
            print("-" * 55)
        turns_this_run = 0
        while (
            not self.game.game_over
            and turns_this_run < max_turns
        ):
            record = self.step()
            turns_this_run += 1
            if verbose:
                print(
                    f"Turn {record.turn_number:03d}: "
                    f"{record.message}"
                )
        result = self.get_results()
        if verbose:
            print("\n" + "=" * 55)
            print("MATCH RESULTS")
            print("=" * 55)
            if result["winner"] is not None:
                print(f"Winner: {result['winner']}")
            else:
                print(
                    "No winner: turn limit reached."
                )
            print(f"Total turns: {result['total_turns']}")
            print("\nRemaining hand points:")
            for name, points in result["hand_points"].items():
                print(f"  {name}: {points}")
        return result

    def get_results(self) -> dict:
        """Summarize the current match state."""
        winner = self.game.winner
        return {
            "winner": winner.name if winner else None,
            "completed": self.game.game_over,
            "total_turns": self.game.turn_count,
            "hand_points": {
                player.name: player.hand_points()
                for player in self.game.players
            },
            "decision_times_ms": {
                player.name: [
                    record.decision_time_ms
                    for record in self.turn_history
                    if record.player_id == player.player_id
                ]
                for player in self.game.players
            },
        }
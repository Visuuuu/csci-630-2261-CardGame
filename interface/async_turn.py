import queue
import threading
from time import perf_counter
from agents.base_agent import AgentDecision
from interface.game_controller import (
    GameController,
    TurnRecord,
)


class AsyncTurnRunner:
    """Calculate AI decisions without blocking Tkinter.
    Request and poll must be called on the GUI thread.
    Only choose_action runs on a background thread.
    """
    def __init__(self, controller: GameController):
        self.controller = controller
        self._results = queue.SimpleQueue()
        self._busy = False
        self._closed = False

        self._player_id = None
        self._player_name = None

    @property
    def is_busy(self) -> bool:
        return self._busy

    def request_turn(self) -> None:
        """Start calculating one AI decision."""
        if self._closed:
            raise RuntimeError("Turn runner is closed.")
        if self._busy:
            raise RuntimeError(
                "An AI decision is already running."
            )
        if self.controller.game.game_over:
            raise ValueError("The game is already over.")
        game = self.controller.game
        player = game.current_player
        # Create the restricted observation on
        # the main thread before launching the worker.
        observation = self.controller._create_observation()
        agent = self.controller.agents[player.player_id]
        self._player_id = player.player_id
        self._player_name = player.name
        self._busy = True
        def worker():
            start = perf_counter()
            try:
                decision = agent.choose_action(observation)
                elapsed_ms = (
                    perf_counter() - start
                ) * 1000
                self._results.put(
                    (decision, elapsed_ms, None)
                )
            except Exception as error:
                self._results.put(
                    (None, 0.0, error)
                )
        thread = threading.Thread(
            target=worker,
            daemon=True,
            name="UNO-AI-Worker",
        )
        thread.start()

    def poll(self) -> TurnRecord | None:
        """Apply a completed decision on the GUI thread.
        Returns None while the AI is still computing.
        """
        if not self._busy or self._closed:
            return None
        try:
            decision, elapsed_ms, error = (
                self._results.get_nowait()
            )
        except queue.Empty:
            return None
        self._busy = False
        if error is not None:
            raise error
        if not isinstance(decision, AgentDecision):
            raise TypeError(
                "Agent must return an AgentDecision."
            )
        # The real game state changes only here,
        # on the main GUI thread.
        game = self.controller.game
        if game.current_player_index != self._player_id:
            raise RuntimeError(
                "Current player changed during AI decision."
            )
        message = game.play_turn(
            card=decision.card,
            chosen_color=decision.chosen_color,
        )
        record = TurnRecord(
            turn_number=game.turn_count,
            player_id=self._player_id,
            player_name=self._player_name,
            message=message,
            decision_time_ms=elapsed_ms,
        )
        self.controller.turn_history.append(record)
        return record

    def close(self) -> None:
        """Invalidate this runner when closing the GUI."""
        self._closed = True
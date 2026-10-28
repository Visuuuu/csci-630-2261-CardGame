import threading
import time
import unittest
from agents.base_agent import (
    AgentDecision,
    AgentObservation,
    BaseAgent,
)
from interface.async_turn import AsyncTurnRunner
from interface.game_controller import GameController, TurnRecord
from uno_game.card import CardType, Color


class ControlledAgent(BaseAgent):
    """A test agent whose decision can be delayed."""
    def __init__(self, gate=None):
        self.gate = gate
        self.worker_thread_id = None

    def choose_action(
        self,
        observation: AgentObservation,
    ) -> AgentDecision:
        self.worker_thread_id = threading.get_ident()
        if self.gate is not None:
            if not self.gate.wait(timeout=2):
                raise RuntimeError("Test gate timed out.")
        if not observation.legal_cards:
            return AgentDecision(card=None)
        card = observation.legal_cards[0]
        if card.card_type == CardType.WILD:
            return AgentDecision(
                card=card,
                chosen_color=Color.RED,
            )
        return AgentDecision(card=card)


class InvalidAgent(BaseAgent):
    """An agent that deliberately returns invalid output."""
    def choose_action(self, observation):
        return "not an AgentDecision"


class TestAsyncTurnRunner(unittest.TestCase):
    def make_runner(self, first_agent=None):
        agents = [
            first_agent or ControlledAgent(),
            ControlledAgent(),
            ControlledAgent(),
            ControlledAgent(),
        ]
        controller = GameController(
            agents=agents,
            player_names=["P0", "P1", "P2", "P3"],
            seed=42,
        )
        return AsyncTurnRunner(controller)

    def wait_for_result(self, runner):
        """Poll until a completed turn is available."""
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            record = runner.poll()
            if record is not None:
                return record
            time.sleep(0.005)
        self.fail("Background AI decision did not finish.")

    def test_background_turn_completes(self):
        runner = self.make_runner()
        runner.request_turn()
        record = self.wait_for_result(runner)
        self.assertIsInstance(record, TurnRecord)
        self.assertEqual(record.turn_number, 1)
        self.assertFalse(runner.is_busy)

    def test_ai_runs_on_worker_thread(self):
        agent = ControlledAgent()
        runner = self.make_runner(agent)
        main_thread_id = threading.get_ident()
        runner.request_turn()
        self.wait_for_result(runner)
        self.assertNotEqual(
            agent.worker_thread_id,
            main_thread_id,
        )

    def test_game_changes_only_after_poll(self):
        gate = threading.Event()
        runner = self.make_runner(
            ControlledAgent(gate)
        )
        runner.request_turn()
        # A turn is pending, but game state is unchanged.
        self.assertTrue(runner.is_busy)
        self.assertEqual(
            runner.controller.game.turn_count, 0
        )
        self.assertIsNone(runner.poll())
        gate.set()
        record = self.wait_for_result(runner)
        self.assertEqual(record.turn_number, 1)
        self.assertEqual(
            runner.controller.game.turn_count, 1
        )

    def test_cannot_start_overlapping_turns(self):
        gate = threading.Event()
        runner = self.make_runner(
            ControlledAgent(gate)
        )
        runner.request_turn()
        with self.assertRaises(RuntimeError):
            runner.request_turn()
        gate.set()
        self.wait_for_result(runner)

    def test_turn_history_records_decision_time(self):
        runner = self.make_runner()
        runner.request_turn()
        record = self.wait_for_result(runner)
        self.assertGreaterEqual(
            record.decision_time_ms, 0
        )
        self.assertEqual(
            runner.controller.turn_history,
            [record],
        )

    def test_invalid_agent_result_is_rejected(self):
        runner = self.make_runner(
            InvalidAgent()
        )
        runner.request_turn()
        deadline = time.monotonic() + 3.0
        while runner.is_busy and time.monotonic() < deadline:
            try:
                runner.poll()
            except TypeError:
                break
            time.sleep(0.005)
        else:
            self.fail("Expected invalid decision to raise TypeError.")
        self.assertEqual(
            runner.controller.game.turn_count, 0
        )

    def test_closed_runner_rejects_new_turns(self):
        runner = self.make_runner()
        runner.close()
        with self.assertRaises(RuntimeError):
            runner.request_turn()


if __name__ == "__main__":
    unittest.main()

import unittest
from agents.base_agent import (
    AgentDecision,
    AgentObservation,
    BaseAgent,
)
from agents.greedy_agent import GreedyAgent
from agents.random_agent import RandomAgent
from interface.game_controller import (
    GameController,
    TurnRecord,
)


class SpyAgent(BaseAgent):
    """Test agent that records its latest observation."""
    def __init__(self):
        self.last_observation = None

    def choose_action(
        self,
        observation: AgentObservation,
    ) -> AgentDecision:
        self.last_observation = observation
        if not observation.legal_cards:
            return AgentDecision(card=None)
        card = observation.legal_cards[0]
        from uno_game.card import CardType, Color
        if card.card_type == CardType.WILD:
            return AgentDecision(
                card=card,
                chosen_color=Color.RED,
            )
        return AgentDecision(card=card)


class TestGameController(unittest.TestCase):
    def setUp(self):
        self.names = [
            "Random 1",
            "Greedy 1",
            "Random 2",
            "Greedy 2",
        ]
        self.agents = [
            RandomAgent(seed=101),
            GreedyAgent(),
            RandomAgent(seed=202),
            GreedyAgent(),
        ]
        self.controller = GameController(
            agents=self.agents,
            player_names=self.names,
            seed=42,
        )

    def test_four_agents_assigned(self):
        self.assertEqual(
            len(self.controller.agents), 4
        )
        self.assertEqual(
            len(self.controller.game.players), 4
        )

    def test_single_step(self):
        record = self.controller.step()
        self.assertIsInstance(record, TurnRecord)
        self.assertEqual(record.turn_number, 1)
        self.assertEqual(self.controller.game.turn_count, 1)
        self.assertEqual(
            len(self.controller.turn_history), 1
        )

    def test_decision_time_recorded(self):
        record = self.controller.step()
        self.assertGreaterEqual(
            record.decision_time_ms, 0
        )

    def test_observation_contains_only_own_hand(self):
        spy = SpyAgent()
        agents = [
            spy,
            GreedyAgent(),
            RandomAgent(seed=3),
            GreedyAgent(),
        ]
        controller = GameController(
            agents=agents,
            player_names=self.names,
            seed=42,
        )
        own_hand = controller.game.players[0].hand
        opponent_hand = controller.game.players[1].hand
        controller.step()
        observation = spy.last_observation
        self.assertEqual(observation.hand, own_hand)
        self.assertNotEqual(
            observation.hand,
            opponent_hand,
        )
        self.assertFalse(
            hasattr(observation, "opponent_hands")
        )
        self.assertFalse(
            hasattr(observation, "deck")
        )
        self.assertFalse(
            hasattr(observation, "game")
        )

    def test_result_structure(self):
        self.controller.step()
        result = self.controller.get_results()
        self.assertIn("winner", result)
        self.assertIn("completed", result)
        self.assertIn("total_turns", result)
        self.assertIn("hand_points", result)
        self.assertIn("decision_times_ms", result)

    def test_turn_limit(self):
        result = self.controller.run_game(
            max_turns=1,
            verbose=False,
        )
        self.assertEqual(result["total_turns"], 1)
        self.assertFalse(result["completed"])
        self.assertIsNone(result["winner"])

    def test_reject_invalid_agent_count(self):
        with self.assertRaises(ValueError):
            GameController(
                agents=[RandomAgent()],
                player_names=self.names,
            )

    def test_reject_invalid_agent_type(self):
        with self.assertRaises(TypeError):
            GameController(
                agents=[
                    RandomAgent(),
                    GreedyAgent(),
                    object(),
                    GreedyAgent(),
                ],
                player_names=self.names,
            )

    def test_full_game_or_turn_limit(self):
        result = self.controller.run_game(
            max_turns=1000,
            verbose=False,
        )
        self.assertLessEqual(result["total_turns"], 1000)
        if result["completed"]:
            self.assertIsNotNone(result["winner"])
            self.assertEqual(
                result["hand_points"][result["winner"]],
                0,
            )
        else:
            self.assertIsNone(result["winner"])


if __name__ == "__main__":
    unittest.main()

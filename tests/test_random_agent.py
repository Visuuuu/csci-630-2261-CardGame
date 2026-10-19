import unittest
from dataclasses import fields
from agents.base_agent import (
    AgentDecision,
    AgentObservation,
    BaseAgent,
)
from agents.random_agent import RandomAgent
from uno_game.card import Card, Color, CardType
from uno_game.rules import get_playable_cards

class TestRandomAgent(unittest.TestCase):
    def setUp(self):
        self.agent = RandomAgent(seed=42)
        self.top_card = Card(
            Color.RED, CardType.NUMBER, 5
        )
        self.red_seven = Card(
            Color.RED, CardType.NUMBER, 7
        )
        self.blue_five = Card(
            Color.BLUE, CardType.NUMBER, 5
        )
        self.green_two = Card(
            Color.GREEN, CardType.NUMBER, 2
        )
        self.wild = Card(
            Color.WILD, CardType.WILD
        )

    def make_observation(self, hand):
        """Build an observation using the rules engine."""
        hand = tuple(hand)
        legal_cards = tuple(
            get_playable_cards(
                hand,
                self.top_card,
                Color.RED,
            )
        )
        return AgentObservation(
            hand=hand,
            legal_cards=legal_cards,
            top_card=self.top_card,
            active_color=Color.RED,
        )

    def test_agent_inherits_base_agent(self):
        self.assertIsInstance(self.agent, BaseAgent)

    def test_returns_agent_decision(self):
        observation = self.make_observation(
            [self.red_seven]
        )
        decision = self.agent.choose_action(observation)
        self.assertIsInstance(decision, AgentDecision)

    def test_selects_legal_card(self):
        observation = self.make_observation([
            self.red_seven,
            self.blue_five,
            self.green_two,
        ])
        decision = self.agent.choose_action(observation)
        self.assertIn(
            decision.card,
            observation.legal_cards,
        )
        self.assertIsNone(decision.chosen_color)

    def test_draws_when_no_legal_cards(self):
        observation = self.make_observation([
            self.green_two
        ])
        decision = self.agent.choose_action(observation)
        self.assertIsNone(decision.card)
        self.assertIsNone(decision.chosen_color)

    def test_wild_color_choice(self):
        observation = self.make_observation([self.wild])
        decision = self.agent.choose_action(observation)
        self.assertEqual(decision.card, self.wild)
        self.assertIn(
            decision.chosen_color,
            (
                Color.RED,
                Color.YELLOW,
                Color.GREEN,
                Color.BLUE,
            ),
        )

    def test_seed_reproducibility(self):
        first_agent = RandomAgent(seed=42)
        second_agent = RandomAgent(seed=42)
        observation = self.make_observation([
            self.red_seven,
            self.blue_five,
            self.wild,
        ])
        first_decisions = [
            first_agent.choose_action(observation)
            for _ in range(20)
        ]
        second_decisions = [
            second_agent.choose_action(observation)
            for _ in range(20)
        ]
        self.assertEqual(
            first_decisions,
            second_decisions,
        )

    def test_observation_contains_no_opponent_hands(self):
        field_names = {
            field.name
            for field in fields(AgentObservation)
        }
        self.assertEqual(
            field_names,
            {
                "hand",
                "legal_cards",
                "top_card",
                "active_color",
            },
        )

    def test_observation_is_immutable(self):
        observation = self.make_observation([
            self.red_seven
        ])
        with self.assertRaises(AttributeError):
            observation.hand = ()

    def test_does_not_modify_hand(self):
        observation = self.make_observation([
            self.red_seven,
            self.blue_five,
        ])
        original_hand = observation.hand
        self.agent.choose_action(observation)
        self.assertEqual(
            observation.hand,
            original_hand,
        )


if __name__ == "__main__":
    unittest.main()

import unittest
from agents.base_agent import (
    AgentDecision,
    AgentObservation,
    BaseAgent,
)
from agents.greedy_agent import GreedyAgent
from uno_game.card import Card, Color, CardType
from uno_game.rules import get_playable_cards


class TestGreedyAgent(unittest.TestCase):
    def setUp(self):
        self.agent = GreedyAgent()

        self.top_card = Card(
            Color.RED, CardType.NUMBER, 5
        )

    def make_observation(
        self,
        hand,
        active_color=Color.RED,
    ):
        hand = tuple(hand)
        legal_cards = tuple(
            get_playable_cards(
                hand,
                self.top_card,
                active_color,
            )
        )
        return AgentObservation(
            hand=hand,
            legal_cards=legal_cards,
            top_card=self.top_card,
            active_color=active_color,
        )

    def test_inherits_base_agent(self):
        self.assertIsInstance(self.agent, BaseAgent)

    def test_returns_agent_decision(self):
        red_five = Card(
            Color.RED, CardType.NUMBER, 5
        )
        observation = self.make_observation([red_five])
        decision = self.agent.choose_action(observation)
        self.assertIsInstance(decision, AgentDecision)

    def test_chooses_highest_point_card(self):
        red_three = Card(
            Color.RED, CardType.NUMBER, 3
        )
        red_nine = Card(
            Color.RED, CardType.NUMBER, 9
        )
        red_skip = Card(
            Color.RED, CardType.SKIP
        )
        observation = self.make_observation([
            red_three,
            red_nine,
            red_skip,
        ])
        decision = self.agent.choose_action(observation)
        self.assertEqual(decision.card, red_skip)
        self.assertIsNone(decision.chosen_color)

    def test_prefers_wild_over_action_card(self):
        red_draw_two = Card(
            Color.RED, CardType.DRAW_TWO
        )
        wild = Card(
            Color.WILD, CardType.WILD
        )

        observation = self.make_observation([
            red_draw_two,
            wild,
        ])
        decision = self.agent.choose_action(observation)
        self.assertEqual(decision.card, wild)

    def test_draws_when_no_legal_cards(self):
        green_two = Card(
            Color.GREEN, CardType.NUMBER, 2
        )
        observation = self.make_observation([green_two])
        decision = self.agent.choose_action(observation)
        self.assertIsNone(decision.card)
        self.assertIsNone(decision.chosen_color)

    def test_selects_most_common_wild_color(self):
        wild = Card(
            Color.WILD, CardType.WILD
        )
        red_three = Card(
            Color.RED, CardType.NUMBER, 3
        )
        blue_two = Card(
            Color.BLUE, CardType.NUMBER, 2
        )
        blue_nine = Card(
            Color.BLUE, CardType.NUMBER, 9
        )
        observation = self.make_observation([
            wild,
            red_three,
            blue_two,
            blue_nine,
        ])
        decision = self.agent.choose_action(observation)
        self.assertEqual(decision.card, wild)
        self.assertEqual(decision.chosen_color, Color.BLUE)

    def test_wild_color_tie_breaker(self):
        wild = Card(
            Color.WILD, CardType.WILD
        )
        red_three = Card(
            Color.RED, CardType.NUMBER, 3
        )
        blue_two = Card(
            Color.BLUE, CardType.NUMBER, 2
        )

        observation = self.make_observation([
            wild,
            red_three,
            blue_two,
        ])
        decision = self.agent.choose_action(observation)
        self.assertEqual(decision.chosen_color, Color.RED)

    def test_deterministic_decisions(self):
        wild = Card(
            Color.WILD, CardType.WILD
        )
        red_eight = Card(
            Color.RED, CardType.NUMBER, 8
        )

        observation = self.make_observation([
            wild,
            red_eight,
        ])
        first = self.agent.choose_action(observation)
        second = self.agent.choose_action(observation)
        self.assertEqual(first, second)

    def test_selects_only_legal_cards(self):
        red_five = Card(
            Color.RED, CardType.NUMBER, 5
        )
        green_nine = Card(
            Color.GREEN, CardType.NUMBER, 9
        )

        observation = self.make_observation([
            red_five,
            green_nine,
        ])
        decision = self.agent.choose_action(observation)
        self.assertIn(
            decision.card,
            observation.legal_cards,
        )

    def test_does_not_modify_hand(self):
        wild = Card(
            Color.WILD, CardType.WILD
        )
        red_four = Card(
            Color.RED, CardType.NUMBER, 4
        )
        observation = self.make_observation([
            wild,
            red_four,
        ])
        original_hand = observation.hand
        self.agent.choose_action(observation)
        self.assertEqual(
            observation.hand,
            original_hand,
        )


if __name__ == "__main__":
    unittest.main()

import unittest
from agents.base_agent import (
    AgentDecision,
    AgentObservation,
    BaseAgent,
)
from agents.heuristic_agent import HeuristicAgent
from uno_game.card import Card, CardType, Color
from uno_game.rules import get_playable_cards


class TestHeuristicAgent(unittest.TestCase):
    def setUp(self):
        self.agent = HeuristicAgent()
        self.top_card = Card(
            Color.RED, CardType.NUMBER, 5
        )

    def make_observation(self, cards):
        hand = tuple(cards)
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

    def test_inherits_base_agent(self):
        self.assertIsInstance(self.agent, BaseAgent)

    def test_returns_valid_decision(self):
        card = Card(Color.RED, CardType.NUMBER, 7)
        observation = self.make_observation([card])
        decision = self.agent.choose_action(observation)
        self.assertIsInstance(decision, AgentDecision)
        self.assertEqual(decision.card, card)

    def test_draws_when_no_legal_cards(self):
        observation = self.make_observation([
            Card(Color.GREEN, CardType.NUMBER, 2)
        ])
        decision = self.agent.choose_action(observation)
        self.assertIsNone(decision.card)
        self.assertIsNone(decision.chosen_color)

    def test_prefers_action_card(self):
        red_eight = Card(
            Color.RED, CardType.NUMBER, 8
        )
        red_skip = Card(
            Color.RED, CardType.SKIP
        )
        blue_three = Card(
            Color.BLUE, CardType.NUMBER, 3
        )
        observation = self.make_observation([
            red_eight,
            red_skip,
            blue_three,
        ])
        decision = self.agent.choose_action(observation)
        self.assertEqual(decision.card, red_skip)

    def test_preserves_wild_when_alternatives_exist(self):
        wild = Card(Color.WILD, CardType.WILD)
        red_seven = Card(
            Color.RED, CardType.NUMBER, 7
        )
        blue_two = Card(
            Color.BLUE, CardType.NUMBER, 2
        )
        green_three = Card(
            Color.GREEN, CardType.NUMBER, 3
        )
        observation = self.make_observation([
            wild,
            red_seven,
            blue_two,
            green_three,
        ])
        decision = self.agent.choose_action(observation)
        self.assertEqual(decision.card, red_seven)

    def test_uses_wild_when_only_legal_card(self):
        wild = Card(Color.WILD, CardType.WILD)
        observation = self.make_observation([
            wild,
            Card(Color.GREEN, CardType.NUMBER, 2),
            Card(Color.BLUE, CardType.NUMBER, 9),
            Card(Color.YELLOW, CardType.NUMBER, 4),
        ])
        decision = self.agent.choose_action(observation)
        self.assertEqual(decision.card, wild)
        self.assertIsNotNone(decision.chosen_color)

    def test_wild_as_final_card(self):
        wild = Card(Color.WILD, CardType.WILD)
        observation = self.make_observation([wild])
        decision = self.agent.choose_action(observation)
        self.assertEqual(decision.card, wild)
        self.assertEqual(decision.chosen_color, Color.RED)

    def test_wild_color_selection(self):
        wild = Card(Color.WILD, CardType.WILD)
        observation = self.make_observation([
            wild,
            Card(Color.BLUE, CardType.NUMBER, 2),
            Card(Color.BLUE, CardType.NUMBER, 7),
            Card(Color.GREEN, CardType.NUMBER, 9),
        ])
        decision = self.agent.choose_action(observation)
        self.assertEqual(decision.card, wild)
        self.assertEqual(decision.chosen_color, Color.BLUE)

    def test_wild_color_tie_breaker(self):
        wild = Card(Color.WILD, CardType.WILD)
        observation = self.make_observation([
            wild,
            Card(Color.RED, CardType.NUMBER, 3),
            Card(Color.BLUE, CardType.NUMBER, 2),
        ])
        decision = self.agent.choose_action(observation)
        self.assertEqual(decision.chosen_color, Color.RED)

    def test_draw_two_has_higher_bonus_than_skip(self):
        draw_two = Card(
            Color.RED, CardType.DRAW_TWO
        )
        skip = Card(
            Color.RED, CardType.SKIP
        )
        observation = self.make_observation([
            draw_two, skip
        ])
        selected = self.agent.choose_action(observation)
        self.assertEqual(selected.card, draw_two)

    def test_deterministic_decision(self):
        observation = self.make_observation([
            Card(Color.RED, CardType.SKIP),
            Card(Color.RED, CardType.NUMBER, 9),
            Card(Color.WILD, CardType.WILD),
        ])
        first = self.agent.choose_action(observation)
        second = self.agent.choose_action(observation)
        self.assertEqual(first, second)

    def test_does_not_modify_hand(self):
        observation = self.make_observation([
            Card(Color.RED, CardType.NUMBER, 4),
            Card(Color.WILD, CardType.WILD),
        ])
        original_hand = observation.hand
        self.agent.choose_action(observation)
        self.assertEqual(observation.hand, original_hand)

    def test_selected_card_is_legal(self):
        observation = self.make_observation([
            Card(Color.RED, CardType.NUMBER, 8),
            Card(Color.GREEN, CardType.NUMBER, 2),
            Card(Color.BLUE, CardType.NUMBER, 5),
        ])
        decision = self.agent.choose_action(observation)
        self.assertIn(
            decision.card,
            observation.legal_cards,
        )


if __name__ == "__main__":
    unittest.main()

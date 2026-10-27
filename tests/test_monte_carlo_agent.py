import unittest
from collections import Counter
from agents.base_agent import (
    AgentDecision,
    AgentObservation,
    BaseAgent,
)
from agents.monte_carlo_agent import (
    MonteCarloAgent,
    create_reference_cards,
)
from uno_game.card import Card, CardType, Color
from uno_game.rules import (
    REGULAR_COLORS,
    get_playable_cards,
)


class TestMonteCarloAgent(unittest.TestCase):
    def setUp(self):
        self.agent = MonteCarloAgent(
            num_simulations=20,
            rollout_depth=4,
            seed=42,
        )
        self.top_card = Card(
            Color.RED, CardType.NUMBER, 5
        )

    def make_observation(self, cards):
        hand = tuple(cards)
        legal = tuple(
            get_playable_cards(
                hand,
                self.top_card,
                Color.RED,
            )
        )
        return AgentObservation(
            hand=hand,
            legal_cards=legal,
            top_card=self.top_card,
            active_color=Color.RED,
        )

    def test_inherits_base_agent(self):
        self.assertIsInstance(self.agent, BaseAgent)

    def test_reference_deck_size(self):
        cards = create_reference_cards()
        self.assertEqual(len(cards), 104)
        self.assertEqual(
            sum(
                card.card_type == CardType.WILD
                for card in cards
            ),
            4,
        )

    def test_invalid_simulation_count(self):
        with self.assertRaises(ValueError):
            MonteCarloAgent(num_simulations=0)

    def test_invalid_rollout_depth(self):
        with self.assertRaises(ValueError):
            MonteCarloAgent(rollout_depth=0)

    def test_returns_legal_action(self):
        observation = self.make_observation([
            Card(Color.RED, CardType.NUMBER, 7),
            Card(Color.BLUE, CardType.NUMBER, 5),
            Card(Color.GREEN, CardType.NUMBER, 2),
        ])
        decision = self.agent.choose_action(
            observation
        )
        self.assertIsInstance(decision, AgentDecision)
        self.assertIn(
            decision.card,
            observation.legal_cards,
        )

    def test_draws_when_no_legal_cards(self):
        observation = self.make_observation([
            Card(Color.GREEN, CardType.NUMBER, 2),
        ])
        decision = self.agent.choose_action(
            observation
        )
        self.assertIsNone(decision.card)
        self.assertIsNone(decision.chosen_color)

    def test_single_legal_card(self):
        red_seven = Card(
            Color.RED, CardType.NUMBER, 7
        )
        observation = self.make_observation([
            red_seven,
            Card(Color.GREEN, CardType.NUMBER, 2),
        ])
        decision = self.agent.choose_action(
            observation
        )
        self.assertEqual(decision.card, red_seven)

    def test_wild_color_is_valid(self):
        wild = Card(Color.WILD, CardType.WILD)
        observation = self.make_observation([
            wild,
            Card(Color.BLUE, CardType.NUMBER, 2),
            Card(Color.GREEN, CardType.NUMBER, 9),
        ])
        decision = self.agent.choose_action(
            observation
        )
        self.assertEqual(decision.card, wild)
        self.assertIn(
            decision.chosen_color,
            REGULAR_COLORS,
        )

    def test_immediate_winning_move(self):
        red_seven = Card(
            Color.RED, CardType.NUMBER, 7
        )
        observation = self.make_observation([
            red_seven
        ])
        decision = self.agent.choose_action(
            observation
        )
        self.assertEqual(decision.card, red_seven)

    def test_reproducible_decisions(self):
        first = MonteCarloAgent(
            num_simulations=20,
            rollout_depth=4,
            seed=123,
        )
        second = MonteCarloAgent(
            num_simulations=20,
            rollout_depth=4,
            seed=123,
        )
        observation = self.make_observation([
            Card(Color.RED, CardType.NUMBER, 8),
            Card(Color.RED, CardType.SKIP),
            Card(Color.WILD, CardType.WILD),
            Card(Color.GREEN, CardType.NUMBER, 2),
        ])
        self.assertEqual(
            first.choose_action(observation),
            second.choose_action(observation),
        )

    def test_unknown_pool_excludes_known_cards(self):
        red_zero = Card(
            Color.RED, CardType.NUMBER, 0
        )
        observation = self.make_observation([
            red_zero,
            Card(Color.BLUE, CardType.NUMBER, 8),
        ])
        unknown = self.agent._unknown_card_pool(
            observation
        )
        counts = Counter(unknown)
        # Only one Red 0 exists in the full deck.
        self.assertEqual(counts[red_zero], 0)
        # One Blue 8 remains out of two.
        blue_eight = Card(
            Color.BLUE, CardType.NUMBER, 8
        )
        self.assertEqual(counts[blue_eight], 1)
        # The visible top Red 5 is excluded once.
        self.assertEqual(
            counts[self.top_card], 1
        )

    def test_does_not_modify_observation(self):
        observation = self.make_observation([
            Card(Color.RED, CardType.NUMBER, 8),
            Card(Color.WILD, CardType.WILD),
        ])
        original_hand = observation.hand
        original_legal = observation.legal_cards
        self.agent.choose_action(observation)
        self.assertEqual(
            observation.hand,
            original_hand,
        )
        self.assertEqual(
            observation.legal_cards,
            original_legal,
        )


if __name__ == "__main__":
    unittest.main()

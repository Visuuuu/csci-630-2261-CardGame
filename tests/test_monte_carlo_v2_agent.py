import unittest
from agents.base_agent import AgentObservation
from agents.monte_carlo_agent import MonteCarloAgent
from agents.monte_carlo_v2_agent import MonteCarloV2Agent
from uno_game.card import Card, CardType, Color
from uno_game.rules import get_playable_cards


class TestMonteCarloV2Agent(unittest.TestCase):
    def setUp(self):
        self.agent = MonteCarloV2Agent(
            num_simulations=5,
            rollout_depth=3,
            seed=42,
        )
        self.top_card = Card(
            Color.RED,
            CardType.NUMBER,
            5,
        )

    def make_observation(self, cards):
        hand = tuple(cards)
        return AgentObservation(
            hand=hand,
            legal_cards=tuple(
                get_playable_cards(
                    hand,
                    self.top_card,
                    Color.RED,
                )
            ),
            top_card=self.top_card,
            active_color=Color.RED,
        )

    def test_inherits_original_monte_carlo(self):
        self.assertIsInstance(
            self.agent,
            MonteCarloAgent,
        )

    def test_invalid_sampled_hand_size(self):
        with self.assertRaises(ValueError):
            MonteCarloV2Agent(
                sampled_hand_size=0
            )

    def test_illegal_opponent_card_not_played(self):
        blue_eight = Card(
            Color.BLUE,
            CardType.NUMBER,
            8,
        )
        unknown = [blue_eight]
        top, active = self.agent._simulate_opponent_move(
            self.top_card,
            Color.RED,
            unknown,
        )
        # Blue 8 cannot be played on Red 5.
        self.assertEqual(top, self.top_card)
        self.assertEqual(active, Color.RED)
        self.assertEqual(unknown, [blue_eight])

    def test_matching_number_can_be_played(self):
        blue_five = Card(
            Color.BLUE,
            CardType.NUMBER,
            5,
        )
        unknown = [blue_five]
        top, active = self.agent._simulate_opponent_move(
            self.top_card,
            Color.RED,
            unknown,
        )
        self.assertEqual(top, blue_five)
        self.assertEqual(active, Color.BLUE)
        self.assertEqual(unknown, [])

    def test_rollout_wild_color_selection(self):
        hand = [
            Card(Color.BLUE, CardType.NUMBER, 2),
            Card(Color.BLUE, CardType.NUMBER, 7),
            Card(Color.RED, CardType.NUMBER, 3),
        ]
        color = self.agent._choose_rollout_color(
            hand
        )
        self.assertEqual(color, Color.BLUE)

    def test_returns_legal_action(self):
        observation = self.make_observation([
            Card(Color.RED, CardType.NUMBER, 8),
            Card(Color.RED, CardType.SKIP),
            Card(Color.GREEN, CardType.NUMBER, 2),
            Card(Color.WILD, CardType.WILD),
        ])
        decision = self.agent.choose_action(
            observation
        )
        self.assertIn(
            decision.card,
            observation.legal_cards,
        )

    def test_wild_color_is_valid(self):
        observation = self.make_observation([
            Card(Color.WILD, CardType.WILD),
            Card(Color.BLUE, CardType.NUMBER, 8),
        ])
        decision = self.agent.choose_action(
            observation
        )
        self.assertEqual(
            decision.card.card_type,
            CardType.WILD,
        )
        self.assertIn(
            decision.chosen_color,
            (
                Color.RED,
                Color.YELLOW,
                Color.GREEN,
                Color.BLUE,
            ),
        )

    def test_reproducible_decision(self):
        first = MonteCarloV2Agent(
            num_simulations=10,
            rollout_depth=3,
            seed=123,
        )
        second = MonteCarloV2Agent(
            num_simulations=10,
            rollout_depth=3,
            seed=123,
        )
        observation = self.make_observation([
            Card(Color.RED, CardType.NUMBER, 9),
            Card(Color.RED, CardType.SKIP),
            Card(Color.WILD, CardType.WILD),
            Card(Color.BLUE, CardType.NUMBER, 3),
        ])
        self.assertEqual(
            first.choose_action(observation),
            second.choose_action(observation),
        )

    def test_does_not_modify_observation(self):
        observation = self.make_observation([
            Card(Color.RED, CardType.NUMBER, 7),
            Card(Color.WILD, CardType.WILD),
            Card(Color.GREEN, CardType.NUMBER, 2),
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

import unittest
from agents.greedy_agent import GreedyAgent
from agents.heuristic_agent import HeuristicAgent
from agents.monte_carlo_agent import (
    MonteCarloAgent,
    create_reference_cards,
)
from agents.random_agent import RandomAgent
from agents.base_agent import AgentObservation
from interface.demo_config import create_demo_controller
from uno_game.card import Card, CardType, Color
from uno_game.deck import Deck
from uno_game.game import UNOGame
from uno_game.rules import get_playable_cards


DRAW_FOUR = Card(
    Color.WILD,
    CardType.WILD_DRAW_FOUR,
)


class TestWildDrawFour(unittest.TestCase):
    def setUp(self):
        self.names = ["P0", "P1", "P2", "P3"]
        self.game = UNOGame(
            self.names,
            seed=42,
            include_draw_four=True,
        )
        self.top_card = Card(
            Color.RED, CardType.NUMBER, 5
        )

    def prepare_hand(self, cards):
        """Set up a controlled current-player scenario."""
        self.game.players[0]._hand = list(cards)
        self.game.discard_pile = [self.top_card]
        self.game.active_color = Color.RED

    def test_card_representation(self):
        self.assertEqual(str(DRAW_FOUR), "Wild Draw Four")
        self.assertEqual(DRAW_FOUR.points(), 50)
        with self.assertRaises(ValueError):
            Card(
                Color.RED,
                CardType.WILD_DRAW_FOUR,
            )

    def test_baseline_deck_remains_104(self):
        deck = Deck(seed=42)
        self.assertEqual(
            deck.remaining_cards(), 104
        )
        self.assertFalse(any(
            card.card_type == CardType.WILD_DRAW_FOUR
            for card in deck.cards
        ))

    def test_extended_deck_has_108_cards(self):
        deck = Deck(
            seed=42,
            include_draw_four=True,
        )
        self.assertEqual(deck.remaining_cards(), 108)
        draw_fours = [
            card
            for card in deck.cards
            if card.card_type == CardType.WILD_DRAW_FOUR
        ]
        self.assertEqual(len(draw_fours), 4)

    def test_illegal_with_matching_color(self):
        self.prepare_hand([
            DRAW_FOUR,
            Card(Color.RED, CardType.NUMBER, 7),
        ])
        self.assertNotIn(
            DRAW_FOUR,
            self.game.get_current_legal_cards(),
        )
        with self.assertRaises(ValueError):
            self.game.play_turn(
                DRAW_FOUR,
                chosen_color=Color.BLUE,
            )
        self.assertEqual(self.game.turn_count, 0)
        self.assertIn(DRAW_FOUR, self.game.players[0].hand)

    def test_legal_with_matching_number_only(self):
        hand = (
            DRAW_FOUR,
            Card(Color.BLUE, CardType.NUMBER, 5),
            Card(Color.GREEN, CardType.SKIP),
        )
        legal = get_playable_cards(
            hand,
            self.top_card,
            Color.RED,
        )
        self.assertIn(DRAW_FOUR, legal)

    def test_legal_with_regular_wild(self):
        hand = (
            DRAW_FOUR,
            Card(Color.WILD, CardType.WILD),
        )
        legal = get_playable_cards(
            hand,
            self.top_card,
            Color.RED,
        )
        self.assertIn(DRAW_FOUR, legal)

    def test_draw_four_penalty_and_skip(self):
        self.prepare_hand([
            DRAW_FOUR,
            Card(Color.BLUE, CardType.NUMBER, 3),
        ])
        before = self.game.players[1].hand_size()
        self.game.play_turn(
            DRAW_FOUR,
            chosen_color=Color.GREEN,
        )
        self.assertEqual(
            self.game.players[1].hand_size(),
            before + 4,
        )
        self.assertEqual(
            self.game.current_player_index, 2
        )
        self.assertEqual(
            self.game.active_color, Color.GREEN
        )

    def test_draw_four_requires_valid_color(self):
        self.prepare_hand([
            DRAW_FOUR,
            Card(Color.BLUE, CardType.NUMBER, 2),
        ])
        with self.assertRaises(ValueError):
            self.game.play_turn(DRAW_FOUR)
        with self.assertRaises(ValueError):
            self.game.play_turn(
                DRAW_FOUR,
                chosen_color=Color.WILD,
            )
        self.assertEqual(self.game.turn_count, 0)

    def test_all_agents_choose_valid_wild_color(self):
        hand = (DRAW_FOUR,)
        observation = AgentObservation(
            hand=hand,
            legal_cards=(DRAW_FOUR,),
            top_card=self.top_card,
            active_color=Color.RED,
        )
        agents = [
            RandomAgent(seed=42),
            GreedyAgent(),
            HeuristicAgent(),
            MonteCarloAgent(
                num_simulations=4,
                rollout_depth=2,
                seed=42,
                include_draw_four=True,
            ),
        ]
        for agent in agents:
            with self.subTest(agent=type(agent).__name__):
                decision = agent.choose_action(
                    observation
                )
                self.assertEqual(
                    decision.card, DRAW_FOUR
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

    def test_extended_game_integration(self):
        controller = create_demo_controller(
            ["Random", "Greedy",
             "Heuristic", "Monte Carlo"],
            game_seed=42,
            mc_simulations=4,
            mc_depth=2,
            include_draw_four=True,
        )
        self.assertEqual(
            controller.game.deck.remaining_cards(),
            79,
        )
        self.assertEqual(
            len(create_reference_cards(True)),
            108,
        )
        self.assertTrue(
            controller.game.include_draw_four
        )


if __name__ == "__main__":
    unittest.main()

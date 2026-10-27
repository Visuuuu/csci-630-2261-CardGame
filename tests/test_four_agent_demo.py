import unittest
from agents.greedy_agent import GreedyAgent
from agents.heuristic_agent import HeuristicAgent
from agents.monte_carlo_agent import MonteCarloAgent
from agents.random_agent import RandomAgent
from interface.four_agent_demo import (
    create_four_agent_controller,
)


class TestFourAgentDemo(unittest.TestCase):
    def setUp(self):
        # Use fewer Monte Carlo simulations in tests
        # so the automated suite remains reasonably fast.
        self.controller = create_four_agent_controller(
            game_seed=42,
            monte_carlo_simulations=8,
            monte_carlo_depth=2,
        )

    def test_four_players_created(self):
        self.assertEqual(
            len(self.controller.game.players), 4
        )
        self.assertEqual(
            len(self.controller.agents), 4
        )

    def test_correct_agent_assignment(self):
        agents = self.controller.agents
        self.assertIsInstance(agents[0], RandomAgent)
        self.assertIsInstance(agents[1], GreedyAgent)
        self.assertIsInstance(agents[2], HeuristicAgent)
        self.assertIsInstance(agents[3], MonteCarloAgent)

    def test_starting_hands(self):
        for player in self.controller.game.players:
            self.assertEqual(player.hand_size(), 7)

    def test_each_agent_takes_a_turn(self):
        """Force one safe legal decision from each agent."""
        # The starting player might play an action
        # that changes the next player's turn.
        # Therefore, test each agent separately.
        for player_index in range(4):
            controller = create_four_agent_controller(
                game_seed=42,
                monte_carlo_simulations=8,
                monte_carlo_depth=2,
            )
            controller.game.current_player_index = (
                player_index
            )
            record = controller.step()
            self.assertEqual(
                record.player_id,
                player_index,
            )
            self.assertEqual(
                controller.game.turn_count, 1
            )
            self.assertGreaterEqual(
                record.decision_time_ms,
                0,
            )

    def test_complete_match_or_turn_limit(self):
        results = self.controller.run_game(
            max_turns=300,
            verbose=False,
        )
        self.assertLessEqual(
            results["total_turns"], 300
        )
        if results["completed"]:
            self.assertIn(
                results["winner"],
                ["Random", "Greedy", "Heuristic", "Monte Carlo"],
            )
        else:
            self.assertIsNone(results["winner"])

    def test_results_contain_all_agents(self):
        self.controller.run_game(
            max_turns=20,
            verbose=False,
        )
        expected = {
            "Random",
            "Greedy",
            "Heuristic",
            "Monte Carlo",
        }
        results = self.controller.get_results()
        self.assertEqual(
            set(results["hand_points"]),
            expected,
        )
        self.assertEqual(
            set(results["decision_times_ms"]),
            expected,
        )

    def test_card_conservation_after_match(self):
        self.controller.run_game(
            max_turns=100,
            verbose=False,
        )
        game = self.controller.game
        total_cards = (
            game.deck.remaining_cards()
            + len(game.discard_pile)
            + sum(
                player.hand_size()
                for player in game.players
            )
        )
        self.assertEqual(total_cards, 104)

    def test_reproducible_outcome(self):
        first = create_four_agent_controller(
            game_seed=42,
            monte_carlo_simulations=8,
            monte_carlo_depth=2,
        )
        second = create_four_agent_controller(
            game_seed=42,
            monte_carlo_simulations=8,
            monte_carlo_depth=2,
        )
        first_result = first.run_game(
            max_turns=100,
            verbose=False,
        )
        second_result = second.run_game(
            max_turns=100,
            verbose=False,
        )
        # Ignore measured execution times.
        self.assertEqual(
            first_result["winner"],
            second_result["winner"],
        )
        self.assertEqual(
            first_result["total_turns"],
            second_result["total_turns"],
        )
        self.assertEqual(
            first_result["hand_points"],
            second_result["hand_points"],
        )


if __name__ == "__main__":
    unittest.main()

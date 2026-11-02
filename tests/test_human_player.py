import unittest
from agents.human_player import HumanPlayer


class TestHumanPlayer(unittest.TestCase):
    def test_default_name(self):
        player = HumanPlayer()
        self.assertEqual(player.name, "Human Player")
        self.assertTrue(player.is_human)

    def test_custom_name(self):
        player = HumanPlayer("Player 1")
        self.assertEqual(player.name, "Player 1")

    def test_human_has_no_ai_decision_method(self):
        player = HumanPlayer()
        self.assertFalse(hasattr(player, "choose_action"))


if __name__ == "__main__":
    unittest.main()

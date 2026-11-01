import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from interface.demo_config import create_demo_controller
from experiments.system_check import (
    BASELINE_LINEUP,
    V1_V2_LINEUP,
    SystemCheckConfig,
    run_smoke_game,
    run_system_checks,
    save_system_report,
    validate_observation,
)


class TestSystemIntegration(unittest.TestCase):
    def setUp(self):
        # Small budgets keep integration tests fast.
        self.config = SystemCheckConfig(
            game_seed=42,
            max_turns=12,
            mc_simulations=2,
            mc_depth=2,
        )

    def test_default_configuration(self):
        config = SystemCheckConfig()
        self.assertEqual(config.game_seed, 42)
        self.assertEqual(config.max_turns, 40)
        self.assertEqual(config.mc_simulations, 3)
        self.assertEqual(config.mc_depth, 2)

    def test_rejects_invalid_configuration(self):
        with self.assertRaises(ValueError):
            SystemCheckConfig(max_turns=0)
        with self.assertRaises(ValueError):
            SystemCheckConfig(mc_simulations=0)
        with self.assertRaises(ValueError):
            SystemCheckConfig(mc_depth=0)

    def test_both_lineups_have_four_agents(self):
        self.assertEqual(len(BASELINE_LINEUP), 4)
        self.assertEqual(len(V1_V2_LINEUP), 4)
        self.assertIn(
            "Monte Carlo V2",
            V1_V2_LINEUP,
        )
        self.assertIn(
            "Monte Carlo",
            BASELINE_LINEUP,
        )

    def test_real_observation_is_restricted(self):
        controller = create_demo_controller(
            agent_types=BASELINE_LINEUP,
            game_seed=42,
            mc_simulations=2,
            mc_depth=2,
        )
        # Raises AssertionError if validation fails.
        validate_observation(controller)
        observation = controller._create_observation()
        self.assertFalse(
            hasattr(observation, "opponent_hands")
        )
        self.assertFalse(
            hasattr(observation, "deck")
        )
        self.assertEqual(
            len(observation.hand),
            7,
        )

    def test_hidden_information_is_detected(self):
        fake_observation = SimpleNamespace(
            hand=(),
            legal_cards=(),
            top_card=None,
            active_color=None,
            opponent_hands=[["secret"]],
        )
        fake_controller = SimpleNamespace(
            _create_observation=(
                lambda: fake_observation
            ),
        )
        with self.assertRaises(AssertionError):
            validate_observation(fake_controller)

    def test_baseline_smoke_game(self):
        result = run_smoke_game(
            lineup=BASELINE_LINEUP,
            include_draw_four=False,
            config=self.config,
        )
        self.assertTrue(result["passed"])
        self.assertEqual(
            result["initial_draw_pile"],
            75,
        )
        self.assertLessEqual(
            result["turns"],
            12,
        )
        self.assertEqual(
            len(result["hand_points"]),
            4,
        )

    def test_extended_v2_smoke_game(self):
        result = run_smoke_game(
            lineup=V1_V2_LINEUP,
            include_draw_four=True,
            config=self.config,
        )
        self.assertTrue(result["passed"])
        self.assertEqual(
            result["initial_draw_pile"],
            79,
        )
        self.assertLessEqual(
            result["turns"],
            12,
        )

    @patch(
        "experiments.system_check.run_smoke_game"
    )
    def test_four_scenarios_are_scheduled(
        self,
        mock_smoke,
    ):
        mock_smoke.return_value = {
            "passed": True,
        }
        report = run_system_checks(self.config)
        self.assertEqual(
            mock_smoke.call_count,
            4,
        )
        self.assertEqual(
            report["scenarios_run"],
            4,
        )
        self.assertEqual(
            report["scenarios_passed"],
            4,
        )
        combinations = {
            (
                tuple(call.kwargs["lineup"]),
                call.kwargs["include_draw_four"],
            )
            for call in mock_smoke.call_args_list
        }
        self.assertEqual(
            combinations,
            {
                (BASELINE_LINEUP, False),
                (V1_V2_LINEUP, False),
                (BASELINE_LINEUP, True),
                (V1_V2_LINEUP, True),
            },
        )

    def test_json_report_export(self):
        report = {
            "scenarios_run": 4,
            "scenarios_passed": 4,
            "results": [],
        }
        with tempfile.TemporaryDirectory() as folder:
            path = save_system_report(
                report,
                Path(folder) / "system_check.json",
            )
            self.assertTrue(path.exists())
            with path.open(
                encoding="utf-8"
            ) as file:
                loaded = json.load(file)
            self.assertEqual(
                loaded,
                report,
            )


if __name__ == "__main__":
    unittest.main()

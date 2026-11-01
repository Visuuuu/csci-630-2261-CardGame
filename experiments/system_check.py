import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from interface.demo_config import create_demo_controller


BASELINE_LINEUP = (
    "Random",
    "Greedy",
    "Heuristic",
    "Monte Carlo",
)

V1_V2_LINEUP = (
    "Monte Carlo",
    "Monte Carlo V2",
    "Greedy",
    "Heuristic",
)


@dataclass(frozen=True)
class SystemCheckConfig:
    """Settings for quick end-to-end integration checks."""
    game_seed: int = 42
    max_turns: int = 40
    mc_simulations: int = 3
    mc_depth: int = 2
    def __post_init__(self):
        if self.max_turns <= 0:
            raise ValueError("max_turns must be positive.")
        if self.mc_simulations <= 0:
            raise ValueError(
                "mc_simulations must be positive."
            )
        if self.mc_depth <= 0:
            raise ValueError("mc_depth must be positive.")


def validate_observation(controller) -> None:
    """Check that an agent receives restricted information."""
    observation = controller._create_observation()
    # These are the permitted observation fields.
    required_fields = (
        "hand",
        "legal_cards",
        "top_card",
        "active_color",
    )
    for field in required_fields:
        if not hasattr(observation, field):
            raise AssertionError(
                f"Missing observation field: {field}"
            )
    # The observation must not expose the game engine,
    # opponent hands, deck, or actual draw pile.
    forbidden_fields = (
        "game",
        "players",
        "opponent_hands",
        "deck",
        "draw_pile",
    )
    for field in forbidden_fields:
        if hasattr(observation, field):
            raise AssertionError(
                f"Hidden information exposed: {field}"
            )
    hand = list(observation.hand)
    legal_cards = list(observation.legal_cards)
    if not all(card in hand for card in legal_cards):
        raise AssertionError(
            "Legal action references a card outside "
            "the current player's hand."
        )


def run_smoke_game(
    lineup: tuple[str, ...],
    include_draw_four: bool,
    config: SystemCheckConfig,
) -> dict:
    """Create and execute one short four-player game."""
    if len(lineup) != 4:
        raise ValueError(
            "A smoke game requires exactly four agents."
        )
    controller = create_demo_controller(
        agent_types=lineup,
        game_seed=config.game_seed,
        mc_simulations=config.mc_simulations,
        mc_depth=config.mc_depth,
        include_draw_four=include_draw_four,
    )
    if len(controller.agents) != 4:
        raise AssertionError(
            "Controller must have four agents."
        )
    if len(controller.game.players) != 4:
        raise AssertionError(
            "Game must have four players."
        )
    player_names = [
        player.name
        for player in controller.game.players
    ]
    if len(set(player_names)) != 4:
        raise AssertionError(
            "Player names must be unique."
        )
    if any(
        len(player.hand) != 7
        for player in controller.game.players
    ):
        raise AssertionError(
            "Each player must start with seven cards."
        )
    expected_remaining = (
        79 if include_draw_four else 75
    )
    actual_remaining = (
        controller.game.deck.remaining_cards()
    )
    if actual_remaining != expected_remaining:
        raise AssertionError(
            "Unexpected initial draw-pile size: "
            f"{actual_remaining}"
        )
    validate_observation(controller)
    result = controller.run_game(
        max_turns=config.max_turns,
        verbose=False,
    )
    turns = result["total_turns"]
    hand_points = result["hand_points"]
    if not 0 <= turns <= config.max_turns:
        raise AssertionError(
            "Turn count exceeds the configured limit."
        )
    if len(hand_points) != 4:
        raise AssertionError(
            "Expected hand points for four players."
        )
    if not all(
        isinstance(points, (int, float))
        and points >= 0
        for points in hand_points.values()
    ):
        raise AssertionError(
            "Invalid remaining hand points."
        )
    return {
        "ruleset": (
            "108-card extended"
            if include_draw_four
            else "104-card baseline"
        ),
        "lineup": list(lineup),
        "seed": config.game_seed,
        "initial_draw_pile": expected_remaining,
        "turns": turns,
        "max_turns": config.max_turns,
        "hand_points": dict(hand_points),
        "passed": True,
    }


def run_system_checks(
    config: SystemCheckConfig,
) -> dict:
    """Exercise both rulesets with two agent lineups."""
    scenarios = [
        (BASELINE_LINEUP, False),
        (V1_V2_LINEUP, False),
        (BASELINE_LINEUP, True),
        (V1_V2_LINEUP, True),
    ]
    results = []
    for lineup, include_draw_four in scenarios:
        result = run_smoke_game(
            lineup=lineup,
            include_draw_four=include_draw_four,
            config=config,
        )
        results.append(result)
    return {
        "check_name": "CSCI 630 UNO System Integration",
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "configuration": asdict(config),
        "scenarios_run": len(results),
        "scenarios_passed": sum(
            1 for row in results if row["passed"]
        ),
        "results": results,
    }


def save_system_report(
    report: dict,
    output_path: str | Path,
) -> Path:
    """Write a readable JSON verification report."""
    path = Path(output_path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )
    return path


def main():
    config = SystemCheckConfig()
    print("=" * 60)
    print("CSCI 630 UNO - FINAL SYSTEM CHECK")
    print("=" * 60)
    report = run_system_checks(config)
    for index, scenario in enumerate(
        report["results"],
        start=1,
    ):
        print(
            f"\nScenario {index}: "
            f"{scenario['ruleset']}"
        )
        print(
            "  Lineup: "
            + ", ".join(scenario["lineup"])
        )
        print(
            f"  Turns: {scenario['turns']}"
        )
        print("  Status: PASS")
    output = save_system_report(
        report,
        Path("reports/system_check.json"),
    )
    print("\n" + "=" * 60)
    print(
        f"Passed: {report['scenarios_passed']}"
        f"/{report['scenarios_run']}"
    )
    print(f"Report: {output.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()

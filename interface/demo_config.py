from agents.base_agent import BaseAgent
from agents.greedy_agent import GreedyAgent
from agents.heuristic_agent import HeuristicAgent
from agents.monte_carlo_agent import MonteCarloAgent
from agents.random_agent import RandomAgent
from interface.game_controller import GameController
from agents.monte_carlo_v2_agent import MonteCarloV2Agent



AGENT_TYPES = (
    "Random",
    "Greedy",
    "Heuristic",
    "Monte Carlo",
    "Monte Carlo V2",
)

# Preserve the original four-player default.
DEFAULT_LINEUP = (
    "Random",
    "Greedy",
    "Heuristic",
    "Monte Carlo",
)

# Convenient classroom demonstration setup.
V1_V2_DEMO_LINEUP = (
    "Monte Carlo",
    "Monte Carlo V2",
    "Greedy",
    "Heuristic",
)



def create_demo_controller(
    agent_types: list[str] | tuple[str, ...],
    game_seed: int = 42,
    mc_simulations: int = 25,
    mc_depth: int = 3,
    include_draw_four: bool = False,
) -> GameController:
    """Create a configurable four-player UNO match."""
    if len(agent_types) != 4:
        raise ValueError(
            "Exactly four agent assignments are required."
        )
    for agent_type in agent_types:
        if agent_type not in AGENT_TYPES:
            raise ValueError(
                f"Unknown agent strategy: {agent_type}"
            )
    if mc_simulations <= 0 or mc_depth <= 0:
        raise ValueError(
            "Monte Carlo settings must be positive."
        )
    agents: list[BaseAgent] = []
    names = []
    for player_id, agent_type in enumerate(agent_types):
        # Player IDs keep names unique, including
        # when two players use the same strategy.
        name = f"P{player_id} - {agent_type}"
        names.append(name)
        if agent_type == "Random":
            agent = RandomAgent(
                seed=game_seed * 100 + player_id
            )
        elif agent_type == "Greedy":
            agent = GreedyAgent()
        elif agent_type == "Heuristic":
            agent = HeuristicAgent()
        elif agent_type == "Monte Carlo":
            # Original Monte Carlo V1
            agent = MonteCarloAgent(
                num_simulations=mc_simulations,
                rollout_depth=mc_depth,
                seed=game_seed * 100 + player_id,
                include_draw_four=include_draw_four,
            )
        elif agent_type == "Monte Carlo V2":
            # Improved legal-transition rollout model
            agent = MonteCarloV2Agent(
                num_simulations=mc_simulations,
                rollout_depth=mc_depth,
                seed=game_seed * 100 + player_id,
                include_draw_four=include_draw_four,
            )
        agents.append(agent)
    return GameController(
        agents=agents,
        player_names=names,
        seed=game_seed,
        include_draw_four=include_draw_four,
    )

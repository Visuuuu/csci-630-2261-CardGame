import random
from agents.base_agent import (
    AgentDecision,
    AgentObservation,
    BaseAgent,
)
from uno_game.card import CardType
from uno_game.rules import REGULAR_COLORS

class RandomAgent(BaseAgent):
    """UNO agent that randomly selects legal moves."""
    def __init__(self, seed: int | None = None):
        # Keep agent randomness separate from the deck.
        self._rng = random.Random(seed)
    def choose_action(
        self,
        observation: AgentObservation,
    ) -> AgentDecision:
        """Choose a random legal card or draw."""
        legal_cards = observation.legal_cards
        # No playable card: choose the draw action.
        if not legal_cards:
            return AgentDecision(card=None)
        # Uniformly select a legal card.
        selected_card = self._rng.choice(legal_cards)
        # A Wild card requires a color selection.
        if selected_card.card_type in (
                CardType.WILD,
                CardType.WILD_DRAW_FOUR,
        ):
            chosen_color = self._rng.choice(REGULAR_COLORS)
            return AgentDecision(
                card=selected_card,
                chosen_color=chosen_color,
            )
        # Regular number/action cards need no color choice.
        return AgentDecision(card=selected_card)
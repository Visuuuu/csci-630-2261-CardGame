from collections import Counter
from agents.base_agent import (
    AgentDecision,
    AgentObservation,
    BaseAgent,
)
from uno_game.card import Card, Color, CardType
from uno_game.rules import REGULAR_COLORS

class GreedyAgent(BaseAgent):
    """Choose legal cards that remove the most hand points."""
    def choose_action(
        self,
        observation: AgentObservation,
    ) -> AgentDecision:
        """Select the highest-point legal card."""
        legal_cards = observation.legal_cards
        # No playable cards: draw one card.
        if not legal_cards:
            return AgentDecision(card=None)
        # max() chooses the first card when scores tie.
        selected_card = max(
            legal_cards,
            key=lambda card: card.points(),
        )
        # Wild cards need an active color selection.
        if selected_card.card_type == CardType.WILD:
            chosen_color = self._choose_wild_color(
                observation.hand,
                selected_card,
            )
            return AgentDecision(
                card=selected_card,
                chosen_color=chosen_color,
            )
        return AgentDecision(card=selected_card)

    def _choose_wild_color(
        self,
        hand: tuple[Card, ...],
        selected_card: Card,
    ) -> Color:
        """Choose the most common remaining regular color."""
        remaining_cards = list(hand)
        # Remove one occurrence of the selected Wild.
        remaining_cards.remove(selected_card)
        color_counts = Counter(
            card.color
            for card in remaining_cards
            if card.color in REGULAR_COLORS
        )
        # Deterministic tie priority:
        # Red, Yellow, Green, Blue.
        return max(
            REGULAR_COLORS,
            key=lambda color: color_counts[color],
        )
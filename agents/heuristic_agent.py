from collections import Counter
from agents.base_agent import (
    AgentDecision,
    AgentObservation,
    BaseAgent,
)
from uno_game.card import Card, CardType, Color
from uno_game.rules import REGULAR_COLORS


class HeuristicAgent(BaseAgent):
    """Choose UNO actions using a weighted rule-based score."""
    # Initial heuristic weights.
    POINT_WEIGHT = 0.2
    COLOR_WEIGHT = 3.0
    ACTION_BONUSES = {
        CardType.SKIP: 6.0,
        CardType.REVERSE: 4.0,
        CardType.DRAW_TWO: 8.0,
    }
    WILD_PENALTY = -18.0
    WILD_ENDGAME_BONUS = 15.0
    WILD_FINISH_BONUS = 30.0

    def choose_action(
        self,
        observation: AgentObservation,
    ) -> AgentDecision:
        """Select the legal card with the highest score."""
        if not observation.legal_cards:
            return AgentDecision(card=None)
        selected_card = max(
            observation.legal_cards,
            key=lambda card: self._evaluate_card(
                card, observation
            ),
        )
        if selected_card.card_type in (
                CardType.WILD,
                CardType.WILD_DRAW_FOUR,
        ):
            chosen_color = self._choose_wild_color(
                observation.hand,
                selected_card,
            )
            return AgentDecision(
                card=selected_card,
                chosen_color=chosen_color,
            )
        return AgentDecision(card=selected_card)

    def _evaluate_card(
        self,
        card: Card,
        observation: AgentObservation,
    ) -> float:
        """Calculate the strategic score of a legal card."""
        score = card.points() * self.POINT_WEIGHT
        remaining_hand = list(observation.hand)
        remaining_hand.remove(card)
        # Wild cards can be useful later.
        if card.card_type in (
                CardType.WILD,
                CardType.WILD_DRAW_FOUR,
        ):
            score += self.WILD_PENALTY
            # Wild cards become more useful to play
            # near the end of the game.
            if len(observation.hand) <= 3:
                score += self.WILD_ENDGAME_BONUS
            if len(observation.hand) == 1:
                score += self.WILD_FINISH_BONUS
            return score

        # Prefer leaving cards that match the new
        # active color after this play.
        same_color_count = sum(
            remaining_card.color == card.color
            for remaining_card in remaining_hand
        )
        score += (
            same_color_count * self.COLOR_WEIGHT
        )
        # Action cards can affect opponents' turns.
        score += self.ACTION_BONUSES.get(
            card.card_type, 0.0
        )
        return score

    def _choose_wild_color(
        self,
        hand: tuple[Card, ...],
        selected_card: Card,
    ) -> Color:
        """Choose the most frequent remaining color."""
        remaining_hand = list(hand)
        remaining_hand.remove(selected_card)
        color_counts = Counter(
            card.color
            for card in remaining_hand
            if card.color in REGULAR_COLORS
        )
        # Ties resolve in Red, Yellow, Green, Blue order.
        return max(
            REGULAR_COLORS,
            key=lambda color: color_counts[color],
        )
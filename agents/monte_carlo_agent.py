import random
from collections import Counter
from agents.base_agent import (
    AgentDecision,
    AgentObservation,
    BaseAgent,
)
from uno_game.card import Card, CardType, Color
from uno_game.rules import REGULAR_COLORS, get_playable_cards


def create_reference_cards() -> list[Card]:
    """Build a standard 104-card pool for simulations.
    This is a fresh reference pool, NOT the live draw pile.
    """
    cards = []
    for color in REGULAR_COLORS:
        cards.append(Card(color, CardType.NUMBER, 0))
        for number in range(1, 10):
            for _ in range(2):
                cards.append(
                    Card(color, CardType.NUMBER, number)
                )
        for card_type in (
            CardType.SKIP,
            CardType.REVERSE,
            CardType.DRAW_TWO,
        ):
            for _ in range(2):
                cards.append(Card(color, card_type))
    for _ in range(4):
        cards.append(Card(Color.WILD, CardType.WILD))
    return cards


class MonteCarloAgent(BaseAgent):
    """Evaluate legal moves using randomized hand rollouts.
    This approximation does not simulate complete
    four-player UNO games or reveal opponents' hands.
    """
    def __init__(
        self,
        num_simulations: int = 100,
        rollout_depth: int = 6,
        seed: int | None = None,
    ):
        if num_simulations <= 0:
            raise ValueError(
                "num_simulations must be positive."
            )
        if rollout_depth <= 0:
            raise ValueError(
                "rollout_depth must be positive."
            )
        self.num_simulations = num_simulations
        self.rollout_depth = rollout_depth
        self._rng = random.Random(seed)
        # Fixed deck composition, not an actual UNOGame.
        self._reference_cards = tuple(
            create_reference_cards()
        )

    def choose_action(
        self,
        observation: AgentObservation,
    ) -> AgentDecision:
        """Choose the action with the best simulated value."""
        if not observation.legal_cards:
            return AgentDecision(card=None)
        candidates = []
        # Equal-valued duplicate cards lead to the
        # same resulting hand, so evaluate them once.
        for card in dict.fromkeys(observation.legal_cards):
            if card.card_type == CardType.WILD:
                for color in REGULAR_COLORS:
                    candidates.append(
                        AgentDecision(
                            card=card,
                            chosen_color=color,
                        )
                    )
            else:
                candidates.append(
                    AgentDecision(card=card)
                )
        best_decision = None
        best_score = float("-inf")
        for decision in candidates:
            score = self._evaluate_action(
                observation,
                decision,
            )
            if score > best_score:
                best_score = score
                best_decision = decision
        return best_decision

    def _unknown_card_pool(
        self,
        observation: AgentObservation,
    ) -> list[Card]:
        """Exclude known cards from the reference pool.

        Previously discarded cards are not available
        in our current observation, so this is only
        an approximate unseen-card distribution.
        """
        counts = Counter(self._reference_cards)
        for card in observation.hand:
            counts[card] -= 1
        counts[observation.top_card] -= 1
        return list(counts.elements())

    def _evaluate_action(
        self,
        observation: AgentObservation,
        decision: AgentDecision,
    ) -> float:
        """Average the outcomes of multiple rollouts."""
        total_score = 0.0
        for _ in range(self.num_simulations):
            total_score += self._rollout(
                observation,
                decision,
            )
        return total_score / self.num_simulations

    def _rollout(
        self,
        observation: AgentObservation,
        decision: AgentDecision,
    ) -> float:
        """Simulate possible future changes to our own hand."""
        remaining_hand = list(observation.hand)
        remaining_hand.remove(decision.card)
        # Playing the last card immediately wins
        # under our current UNOGame rules.
        if not remaining_hand:
            return 500.0
        unknown_cards = self._unknown_card_pool(
            observation
        )
        top_card = decision.card
        active_color = (
            decision.chosen_color
            if decision.chosen_color is not None
            else decision.card.color
        )
        for step in range(self.rollout_depth):
            # Approximate an opponent's intervening
            # turn: sometimes the active card/color
            # remains, sometimes it changes.
            if unknown_cards and self._rng.random() < 0.5:
                next_card = self._rng.choice(
                    unknown_cards
                )
                unknown_cards.remove(next_card)
                top_card = next_card
                if next_card.card_type == CardType.WILD:
                    active_color = self._rng.choice(
                        REGULAR_COLORS
                    )
                else:
                    active_color = next_card.color
            legal_cards = get_playable_cards(
                remaining_hand,
                top_card,
                active_color,
            )
            if legal_cards:
                # Use a simple greedy continuation
                # policy within each rollout.
                selected = max(
                    legal_cards,
                    key=lambda card: card.points(),
                )
                remaining_hand.remove(selected)
                top_card = selected
                if selected.card_type == CardType.WILD:
                    active_color = self._rng.choice(
                        REGULAR_COLORS
                    )
                else:
                    active_color = selected.color
                if not remaining_hand:
                    # Reward earlier simulated finishes.
                    return 500.0 - 10.0 * (step + 1)
            elif unknown_cards:
                # Same simplified draw rule as
                # our existing game engine:
                # draw one card and end the turn.
                drawn = self._rng.choice(unknown_cards)
                unknown_cards.remove(drawn)
                remaining_hand.append(drawn)
            else:
                break
        remaining_points = sum(
            card.points() for card in remaining_hand
        )
        # Smaller remaining hands are preferable.
        return (
            -remaining_points
            - 2.0 * len(remaining_hand)
        )
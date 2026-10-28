from collections import Counter
from agents.base_agent import AgentObservation, AgentDecision
from agents.monte_carlo_agent import MonteCarloAgent
from uno_game.card import Card, CardType, Color
from uno_game.rules import REGULAR_COLORS, get_playable_cards


WILD_TYPES = (
    CardType.WILD,
    CardType.WILD_DRAW_FOUR,
)


class MonteCarloV2Agent(MonteCarloAgent):
    """Monte Carlo agent with legal sampled opponent moves.
    Uses only AgentObservation and a hypothetical
    unseen-card pool. Does not inspect real opponents.
    """
    def __init__(
        self,
        num_simulations: int = 100,
        rollout_depth: int = 6,
        seed: int | None = None,
        include_draw_four: bool = False,
        sampled_hand_size: int = 7,
    ):
        super().__init__(
            num_simulations=num_simulations,
            rollout_depth=rollout_depth,
            seed=seed,
            include_draw_four=include_draw_four,
        )
        if sampled_hand_size <= 0:
            raise ValueError(
                "sampled_hand_size must be positive."
            )
        self.sampled_hand_size = sampled_hand_size

    @staticmethod
    def _choose_rollout_color(
        remaining_hand: list[Card],
    ) -> Color:
        """Choose the most frequent regular color."""
        counts = Counter(
            card.color
            for card in remaining_hand
            if card.color in REGULAR_COLORS
        )
        # Deterministic tie-breaking:
        # Red, Yellow, Green, Blue.
        return max(
            REGULAR_COLORS,
            key=lambda color: counts[color],
        )

    def _simulate_opponent_move(
        self,
        top_card: Card,
        active_color: Color,
        unknown_cards: list[Card],
    ) -> tuple[Card, Color]:
        """Sample a hypothetical opponent's legal move.
        Mutates only the local hypothetical unknown pool.
        Never accesses the real game or opponent hands.
        """
        if not unknown_cards:
            return top_card, active_color
        sample_size = min(
            self.sampled_hand_size,
            len(unknown_cards),
        )
        sampled_hand = self._rng.sample(
            unknown_cards,
            sample_size,
        )
        legal_cards = get_playable_cards(
            sampled_hand,
            top_card,
            active_color,
        )
        if not legal_cards:
            # Approximation: the opponent cannot play
            # and the top discard remains unchanged.
            return top_card, active_color
        selected = self._rng.choice(legal_cards)
        # A played card is no longer unseen.
        unknown_cards.remove(selected)
        if selected.card_type in WILD_TYPES:
            remaining_opponent_hand = list(
                sampled_hand
            )
            remaining_opponent_hand.remove(selected)
            chosen_color = self._choose_rollout_color(
                remaining_opponent_hand
            )
            return selected, chosen_color
        return selected, selected.color

    def _rollout(
        self,
        observation: AgentObservation,
        decision: AgentDecision,
    ) -> float:
        """Evaluate a move through hypothetical legal play."""
        remaining_hand = list(observation.hand)
        remaining_hand.remove(decision.card)
        # Match the original agent's immediate-win
        # reward for a final card.
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
            # Simulate one hypothetical opponent move.
            top_card, active_color = (
                self._simulate_opponent_move(
                    top_card,
                    active_color,
                    unknown_cards,
                )
            )
            # Simulate our own next decision.
            legal_cards = get_playable_cards(
                remaining_hand,
                top_card,
                active_color,
            )
            if legal_cards:
                # Keep the original Greedy continuation
                # policy for a controlled comparison.
                selected = max(
                    legal_cards,
                    key=lambda card: card.points(),
                )
                remaining_hand.remove(selected)
                top_card = selected
                if selected.card_type in WILD_TYPES:
                    active_color = (
                        self._choose_rollout_color(
                            remaining_hand
                        )
                    )
                else:
                    active_color = selected.color
                if not remaining_hand:
                    return 500.0 - 10.0 * (step + 1)
            elif unknown_cards:
                # Simplified draw-one-and-pass rule.
                drawn = self._rng.choice(
                    unknown_cards
                )
                unknown_cards.remove(drawn)
                remaining_hand.append(drawn)
            else:
                break
        remaining_points = sum(
            card.points()
            for card in remaining_hand
        )
        return (
            -remaining_points
            - 2.0 * len(remaining_hand)
        )
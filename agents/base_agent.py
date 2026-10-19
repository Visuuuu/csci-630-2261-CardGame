from abc import ABC, abstractmethod
from dataclasses import dataclass
from uno_game.card import Card, Color

@dataclass(frozen=True)
class AgentObservation:
    """Information an AI agent is allowed to see."""
    hand: tuple[Card, ...]
    legal_cards: tuple[Card, ...]
    top_card: Card
    active_color: Color

@dataclass(frozen=True)
class AgentDecision:
    """A card choice and optional Wild color."""
    card: Card | None
    chosen_color: Color | None = None

class BaseAgent(ABC):
    """Common interface for all UNO AI agents."""
    @abstractmethod
    def choose_action(
        self,
        observation: AgentObservation,
    ) -> AgentDecision:
        """Select a legal action from an observation."""
        pass
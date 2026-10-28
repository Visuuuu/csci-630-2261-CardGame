from dataclasses import dataclass
from enum import Enum

class Color(Enum):
    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"
    BLUE = "Blue"
    WILD = "Wild"

class CardType(Enum):
    NUMBER = "Number"
    SKIP = "Skip"
    REVERSE = "Reverse"
    DRAW_TWO = "Draw Two"
    WILD = "Wild"
    WILD_DRAW_FOUR = "Wild Draw Four"


@dataclass(frozen=True)
class Card:
    color: Color
    card_type: CardType
    number: int | None = None

    def __post_init__(self):
        """Validate card attributes."""
        if self.card_type == CardType.NUMBER:
            if self.color == Color.WILD:
                raise ValueError(
                    "Number cards must have a regular color."
                )
            if self.number is None or not 0 <= self.number <= 9:
                raise ValueError(
                    "Number cards must have a value from 0 to 9."
                )
        elif self.card_type == CardType.WILD:
            if self.color != Color.WILD:
                raise ValueError(
                    "Wild cards must have the Wild color."
                )
            if self.number is not None:
                raise ValueError(
                    "Wild cards cannot have a number."
                )
        else:
            if self.color == Color.WILD:
                raise ValueError(
                    "Action cards must have a regular color."
                )
            if self.number is not None:
                raise ValueError(
                    "Action cards cannot have a number."
                )

    def __str__(self):
        """Return a readable card description."""
        if self.card_type == CardType.NUMBER:
            return f"{self.color.value} {self.number}"
        if self.card_type == CardType.WILD:
            return "Wild"
        return f"{self.color.value} {self.card_type.value}"

    def points(self) -> int:
        """Return the penalty points of the card."""
        if self.card_type == CardType.NUMBER:
            return self.number
        if self.card_type == CardType.WILD:
            return 50
        return 20

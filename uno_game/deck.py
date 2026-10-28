import random

from uno_game.card import Card, Color, CardType

class Deck:
    """Manage a deck of UNO cards."""
    def __init__(
        self,
        seed: int | None = None,
        include_draw_four: bool = False,
    ):
        self._rng = random.Random(seed)
        self.include_draw_four = include_draw_four
        self.cards: list[Card] = []
        self._create_deck()
        self.shuffle()

    def _create_deck(self):
        """Create the initial 104-card UNO deck."""
        colors = [
            Color.RED,
            Color.YELLOW,
            Color.GREEN,
            Color.BLUE,
        ]
        for color in colors:
            # One zero card for each color
            self.cards.append(
                Card(color, CardType.NUMBER, 0)
            )
            # Two copies of numbers 1 through 9
            for number in range(1, 10):
                for _ in range(2):
                    self.cards.append(
                        Card(color, CardType.NUMBER, number)
                    )
            # Two copies of each action card
            action_types = [
                CardType.SKIP,
                CardType.REVERSE,
                CardType.DRAW_TWO,
            ]
            for card_type in action_types:
                for _ in range(2):
                    self.cards.append(
                        Card(color, card_type)
                    )
        # Four regular Wild cards
        for _ in range(4):
            self.cards.append(
                Card(Color.WILD, CardType.WILD)
            )
        # Optional Wild Draw Four cards.
        if self.include_draw_four:
            for _ in range(4):
                self.cards.append(
                    Card(
                        Color.WILD,
                        CardType.WILD_DRAW_FOUR,
                    )
                )

    def shuffle(self):
        """Shuffle the cards in place."""
        self._rng.shuffle(self.cards)

    def draw(self) -> Card:
        """Remove and return one card from the deck."""
        if not self.cards:
            raise ValueError("Cannot draw from an empty deck.")
        return self.cards.pop()

    def remaining_cards(self) -> int:
        """Return the number of cards left."""
        return len(self.cards)

    def is_empty(self) -> bool:
        """Check whether the deck is empty."""
        return len(self.cards) == 0

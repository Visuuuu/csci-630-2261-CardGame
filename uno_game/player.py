from uno_game.card import Card
from uno_game.deck import Deck

class Player:
    """Represent a player in the UNO game."""
    def __init__(self, player_id: int, name: str):
        if player_id < 0:
            raise ValueError("Player ID cannot be negative.")
        if not name.strip():
            raise ValueError("Player name cannot be empty.")
        self.player_id = player_id
        self.name = name
        self._hand: list[Card] = []

    @property
    def hand(self) -> tuple[Card, ...]:
        """Return a read-only view of the player's hand."""
        return tuple(self._hand)

    def receive_card(self, card: Card) -> None:
        """Add one card to the player's hand."""
        self._hand.append(card)

    def draw_cards(self, deck: Deck, count: int = 1) -> None:
        """Draw cards from the deck into the player's hand."""
        if count < 0:
            raise ValueError("Card count cannot be negative.")
        for _ in range(count):
            self.receive_card(deck.draw())

    def play_card(self, card: Card) -> Card:
        """Remove a specified card from the player's hand."""
        if card not in self._hand:
            raise ValueError(
                f"{self.name} does not have the card {card}."
            )
        self._hand.remove(card)
        return card

    def hand_size(self) -> int:
        """Return the number of cards in the player's hand."""
        return len(self._hand)

    def hand_points(self) -> int:
        """Calculate total points remaining in the hand."""
        return sum(card.points() for card in self._hand)

    def has_uno(self) -> bool:
        """Check whether the player has exactly one card."""
        return self.hand_size() == 1

    def has_won(self) -> bool:
        """Check whether the player has no cards left."""
        return self.hand_size() == 0

    def __str__(self) -> str:
        return (
            f"{self.name} "
            f"(ID: {self.player_id}, "
            f"Cards: {self.hand_size()})"
        )
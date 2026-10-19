
from uno_game.card import Card, Color, CardType
from uno_game.deck import Deck
from uno_game.player import Player


class UNOGame:
    """Manage the state of a four-player UNO game."""
    NUM_PLAYERS = 4
    STARTING_HAND_SIZE = 7
    def __init__(
        self,
        player_names: list[str],
        seed: int | None = None,
    ):
        if len(player_names) != self.NUM_PLAYERS:
            raise ValueError(
                "UNOGame requires exactly four players."
            )
        if len(set(player_names)) != self.NUM_PLAYERS:
            raise ValueError(
                "All player names must be unique."
            )
        self.players = [
            Player(player_id=i, name=name)
            for i, name in enumerate(player_names)
        ]
        self.deck = Deck(seed=seed)
        self.discard_pile: list[Card] = []
        self.current_player_index = 0
        # 1 = clockwise, -1 = counterclockwise
        self.direction = 1
        self.active_color: Color | None = None
        self.game_over = False
        self.winner: Player | None = None
        self._deal_initial_cards()
        self._initialize_discard_pile()

    def _deal_initial_cards(self) -> None:
        """Deal seven cards to each player."""
        for _ in range(self.STARTING_HAND_SIZE):
            for player in self.players:
                player.draw_cards(self.deck, 1)

    def _initialize_discard_pile(self) -> None:
        """Choose a starting number card."""
        deferred_cards: list[Card] = []
        while True:
            card = self.deck.draw()
            if card.card_type == CardType.NUMBER:
                self.discard_pile.append(card)
                self.active_color = card.color
                break
            deferred_cards.append(card)
        # Return unused action/Wild cards to the draw pile.
        self.deck.cards.extend(deferred_cards)
        self.deck.shuffle()

    @property
    def current_player(self) -> Player:
        """Return the player whose turn is next."""
        return self.players[self.current_player_index]

    @property
    def top_card(self) -> Card:
        """Return the top card of the discard pile."""
        return self.discard_pile[-1]

    def get_next_player_index(self) -> int:
        """Calculate the next player's index."""
        return (
            self.current_player_index + self.direction
        ) % self.NUM_PLAYERS

    def __str__(self) -> str:
        return (
            f"UNO Game | "
            f"Current Player: {self.current_player.name} | "
            f"Direction: {self.direction} | "
            f"Top Card: {self.top_card} | "
            f"Active Color: {self.active_color.value}"
        )
from uno_game.card import Card, Color, CardType
from uno_game.deck import Deck
from uno_game.player import Player
from uno_game.rules import (
    get_playable_cards,
    is_valid_color_choice,
)


class UNOGame:
    """Manage a four-player UNO game."""
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
        self.direction = 1
        self.active_color: Color | None = None
        self.game_over = False
        self.winner: Player | None = None
        self.turn_count = 0
        self._deal_initial_cards()
        self._initialize_discard_pile()

    def _deal_initial_cards(self) -> None:
        """Deal seven cards to each player."""
        for _ in range(self.STARTING_HAND_SIZE):
            for player in self.players:
                player.draw_cards(self.deck, 1)

    def _initialize_discard_pile(self) -> None:
        """Start with a number card."""
        deferred_cards = []
        while True:
            card = self.deck.draw()
            if card.card_type == CardType.NUMBER:
                self.discard_pile.append(card)
                self.active_color = card.color
                break
            deferred_cards.append(card)
        self.deck.cards.extend(deferred_cards)
        self.deck.shuffle()

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    @property
    def top_card(self) -> Card:
        return self.discard_pile[-1]

    def get_next_player_index(self) -> int:
        return (
            self.current_player_index + self.direction
        ) % self.NUM_PLAYERS

    def _advance_turn(self, steps: int = 1) -> None:
        """Move to the next player."""
        self.current_player_index = (
            self.current_player_index
            + self.direction * steps
        ) % self.NUM_PLAYERS

    def get_current_legal_cards(self) -> list[Card]:
        """Get legal cards for the current player."""
        return get_playable_cards(
            self.current_player.hand,
            self.top_card,
            self.active_color,
        )

    def _recycle_discard_pile(self) -> None:
        """Recycle all discards except the top card."""
        if len(self.discard_pile) <= 1:
            return
        top = self.discard_pile.pop()
        self.deck.cards.extend(self.discard_pile)
        self.discard_pile = [top]
        self.deck.shuffle()

    def _draw_one(self, player: Player) -> bool:
        """Draw one card, recycling discards if necessary.

        Return False if no card can be drawn.
        """
        if self.deck.is_empty():
            self._recycle_discard_pile()
        if self.deck.is_empty():
            return False
        player.receive_card(self.deck.draw())
        return True

    def _apply_card_effect(self, card: Card) -> int:
        """Apply a card effect and return turn steps."""
        if card.card_type == CardType.SKIP:
            return 2
        if card.card_type == CardType.REVERSE:
            self.direction *= -1
            return 1
        if card.card_type == CardType.DRAW_TWO:
            next_index = self.get_next_player_index()
            next_player = self.players[next_index]
            for _ in range(2):
                if not self._draw_one(next_player):
                    break
            return 2
        return 1

    def play_turn(
        self,
        card: Card | None = None,
        chosen_color: Color | None = None,
    ) -> str:
        """Execute one complete player turn.

        Card=None means draw when no legal card exists.
        """
        if self.game_over:
            raise ValueError("The game is already over.")
        player = self.current_player
        legal_cards = self.get_current_legal_cards()
        # No card selected: draw one and pass.
        if card is None:
            if legal_cards:
                raise ValueError(
                    "A playable card exists. Select a card."
                )
            drew_card = self._draw_one(player)
            self.turn_count += 1
            self._advance_turn()
            if drew_card:
                return f"{player.name} draws one card."
            return f"{player.name} passes (no cards left to draw)."
        # Reject illegal plays before changing state.
        if card not in legal_cards:
            raise ValueError(
                f"Illegal move: {player.name} cannot play {card}."
            )
        if card.card_type == CardType.WILD:
            if chosen_color is None:
                raise ValueError(
                    "A Wild card requires a chosen color."
                )
            if not is_valid_color_choice(chosen_color):
                raise ValueError(
                    "Invalid color choice for Wild card."
                )
        elif chosen_color is not None:
            raise ValueError(
                "A color may only be chosen for a Wild card."
            )
        # Play the card.
        player.play_card(card)
        self.discard_pile.append(card)
        if card.card_type == CardType.WILD:
            self.active_color = chosen_color
        else:
            self.active_color = card.color
        self.turn_count += 1
        message = f"{player.name} plays {card}."
        if card.card_type == CardType.WILD:
            message += f" Chooses {chosen_color.value}."
        # A player wins immediately after playing
        # their final card.
        if player.has_won():
            self.game_over = True
            self.winner = player
            message += f" {player.name} wins!"
            return message
        # Automatically announce UNO.
        if player.has_uno():
            message += f" {player.name} says UNO!"
        steps = self._apply_card_effect(card)
        self._advance_turn(steps)
        return message

    def __str__(self) -> str:
        return (
            f"UNO Game | "
            f"Current Player: {self.current_player.name} | "
            f"Direction: {self.direction} | "
            f"Top Card: {self.top_card} | "
            f"Active Color: {self.active_color.value}"
        )

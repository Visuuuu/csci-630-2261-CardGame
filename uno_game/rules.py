from uno_game.card import Card, Color, CardType

REGULAR_COLORS = (
    Color.RED,
    Color.YELLOW,
    Color.GREEN,
    Color.BLUE,
)

def is_playable(
    card: Card,
    top_card: Card,
    active_color: Color,
    hand: tuple[Card, ...] | list[Card] | None = None,
) -> bool:
    """Determine whether a card is legally playable."""
    if active_color not in REGULAR_COLORS:
        raise ValueError("Invalid active color.")
    if card.card_type == CardType.WILD:
        return True
    if card.card_type == CardType.WILD_DRAW_FOUR:
        # A Wild Draw Four requires knowledge of the
        # player's own hand to validate legality.
        if hand is None:
            return False
        if card not in hand:
            return False
        return not any(
            held_card.color == active_color
            for held_card in hand
        )
    if card.color == active_color:
        return True
    if (
        card.card_type == CardType.NUMBER
        and top_card.card_type == CardType.NUMBER
        and card.number == top_card.number
    ):
        return True
    if (
        card.card_type == top_card.card_type
        and card.card_type in (
            CardType.SKIP,
            CardType.REVERSE,
            CardType.DRAW_TWO,
        )
    ):
        return True
    return False


def get_playable_cards(
    hand: tuple[Card, ...] | list[Card],
    top_card: Card,
    active_color: Color,
) -> list[Card]:
    """Return cards that the player may legally play."""
    return [
        card
        for card in hand
        if is_playable(
            card,
            top_card,
            active_color,
            hand=hand,
        )
    ]

def is_valid_color_choice(color: Color) -> bool:
    return color in REGULAR_COLORS

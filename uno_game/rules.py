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
) -> bool:
    """Check whether a card can legally be played.

    Args:
        card: The card the player wants to play.
        top_card: The current top card of the discard pile.
        active_color: The color currently in effect.

    Returns:
        True if the card can be played, otherwise False.
    """
    if active_color not in REGULAR_COLORS:
        raise ValueError(
            "Active color must be Red, Yellow, Green, or Blue."
        )
    # Regular Wild cards are always playable.
    if card.card_type == CardType.WILD:
        return True
    # Match the active color.
    if card.color == active_color:
        return True
    # Match the number on the top card.
    if (
        card.card_type == CardType.NUMBER
        and top_card.card_type == CardType.NUMBER
        and card.number == top_card.number
    ):
        return True
    # Match the type of action card.
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
    """Return all playable cards in a player's hand."""
    return [
        card
        for card in hand
        if is_playable(card, top_card, active_color)
    ]

def is_valid_color_choice(color: Color) -> bool:
    """Check whether a color can be selected after a Wild."""
    return color in REGULAR_COLORS

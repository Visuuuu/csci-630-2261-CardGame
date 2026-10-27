from uno_game.card import Card, Color
from uno_game.game import UNOGame


def card_label(card: Card) -> str:
    """Return a short, readable card label."""
    return str(card)


def color_hex(color: Color) -> str:
    """Convert UNO colors to interface colors."""
    colors = {
        Color.RED: "#C73540",
        Color.YELLOW: "#E6AD32",
        Color.GREEN: "#23865B",
        Color.BLUE: "#286AC2",
        Color.WILD: "#303038",
    }
    return colors[color]


def get_game_view(
    game: UNOGame,
    reveal_hands: bool = False,
) -> dict:
    """Build a presentation snapshot of the current game.
    This function is for the user interface only.
    AI agents must continue using AgentObservation.
    """
    players = []
    for player in game.players:
        if reveal_hands:
            visible_cards = [
                card_label(card)
                for card in player.hand
            ]
        else:
            visible_cards = [
                "UNO" for _ in player.hand
            ]
        players.append({
            "name": player.name,
            "player_id": player.player_id,
            "card_count": player.hand_size(),
            "cards": visible_cards,
            "is_current": (
                not game.game_over
                and player.player_id
                == game.current_player_index
            ),
            "has_uno": player.has_uno(),
        })
    return {
        "players": players,
        "top_card": str(game.top_card),
        "top_card_color": color_hex(
            game.top_card.color
        ),
        "active_color": game.active_color.value,
        "active_color_hex": color_hex(
            game.active_color
        ),
        "current_player": (
            None if game.game_over
            else game.current_player.name
        ),
        "direction": (
            "Clockwise"
            if game.direction == 1
            else "Counterclockwise"
        ),
        "turn_count": game.turn_count,
        "deck_count": game.deck.remaining_cards(),
        "game_over": game.game_over,
        "winner": (
            game.winner.name
            if game.winner is not None
            else None
        ),
    }

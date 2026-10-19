from uno_game.game import UNOGame

def main():
    print("=" * 50)
    print("CSCI 630 - Comparative AI Agents")
    print("UNO Strategic Card Game")
    print("=" * 50)
    player_names = [
        "Random Agent",
        "Greedy Agent",
        "Heuristic Agent",
        "Monte Carlo Agent",
    ]
    game = UNOGame(player_names, seed=42)
    print("\nGame initialized successfully!")
    for player in game.players:
        print(f"\n{player.name}:")
        for card in player.hand:
            print(f"  - {card}")
    print("\nStarting Game State")
    print("-" * 30)
    print(f"Top card: {game.top_card}")
    print(f"Active color: {game.active_color.value}")
    print(f"Current player: {game.current_player.name}")
    print(f"Direction: {game.direction}")
    print(f"Cards left in deck: {game.deck.remaining_cards()}")
    print("\nReady to begin gameplay!")

if __name__ == "__main__":
    main()

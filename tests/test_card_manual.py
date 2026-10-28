from uno_game.card import Card, Color, CardType

def main():
    red_five = Card(Color.RED, CardType.NUMBER, 5)
    blue_skip = Card(Color.BLUE, CardType.SKIP)
    green_reverse = Card(Color.GREEN, CardType.REVERSE)
    yellow_draw_two = Card(Color.YELLOW, CardType.DRAW_TWO)
    wild_card = Card(Color.WILD, CardType.WILD)
    cards = [
        red_five,
        blue_skip,
        green_reverse,
        yellow_draw_two,
        wild_card,
    ]
    print("UNO Card Test")
    print("-" * 30)
    for card in cards:
        print(f"{card} -> {card.points()} points")
    assert red_five.points() == 5
    assert blue_skip.points() == 20
    assert green_reverse.points() == 20
    assert yellow_draw_two.points() == 20
    assert wild_card.points() == 50
    print("-" * 30)
    print("All card tests passed!")

if __name__ == "__main__":
    main()

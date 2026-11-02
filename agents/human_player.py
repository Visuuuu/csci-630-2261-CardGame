class HumanPlayer:
    """Represents a player who makes their own moves."""

    is_human = True

    def __init__(self, name="Human Player"):
        self.name = name

    def __repr__(self):
        return f"HumanPlayer(name={self.name!r})"

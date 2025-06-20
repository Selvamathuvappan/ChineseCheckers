from   geometry                 import Point


class Coin:
    """
    Represents a single coin on the board.

    Attributes:
        point (Point): The position of the coin.
        region (int): The region the coin belongs to (equivalent to color).
    """

    def __init__(self, point: Point, region: int):
        assert (
            region != 0
        ), "Coin's region starts from 1, 0 denotes common area that doesn't belong to any player"
        self.point = point
        self.region = region

    def __iter__(self):
        return iter((self.point, self.region))

    def __eq__(self, other):
        return isinstance(other, Coin) and tuple(self) == tuple(other)

    def __hash__(self):
        return hash((self.point, self.region))

    def __str__(self):
        return f"Coin(point={self.point}, region={self.region})"

    def __repr__(self):
        return str(self)

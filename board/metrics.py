from   board.coin               import Coin
from   board.layout             import LayoutInterface
from   geometry                 import Point


class DistanceMetrics:
    """
    Provides distance and heuristic calculations for coins on a Chinese Checkers board.
    """

    def __init__(self, board: LayoutInterface) -> None:
        self.board = board

    @staticmethod
    def distance(src: Point, dst: Point) -> int:
        """Computes the hexagonal grid distance between two points."""
        dx, dy = dst - src
        dx, dy = abs(dx), abs(dy)
        return dy + (dx - dy) // 2 if dx > dy else dy

    def positive_distance(self, coin: Coin, dst: Point) -> int:
        """Computes the signed distance in the 'positive' direction for a coin's region."""
        src = coin.point
        dx, dy = dst - src
        positive_x, positive_y = self.board.positive_direction(coin.region)
        return dx * positive_x + dy * positive_y

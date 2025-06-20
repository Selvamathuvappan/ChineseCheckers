from   board.coin               import Coin
from   board.layout             import LayoutInterface
from   geometry.point           import Point


class DistanceMetrics:

    def __init__(self, board: LayoutInterface):
        self.board = board

    @staticmethod
    def distance(src: Point, dst: Point):
        dx, dy = dst - src
        dx, dy = abs(dx), abs(dy)
        return dy + (dx - dy) // 2 if dx > dy else dy

    def positive_distance(self, coin: Coin, dst: Point) -> int:
        src = coin.point
        dx, dy = dst - src
        positive_x, positive_y = self.board.positive_direction(coin.region)
        return dx * positive_x + dy * positive_y

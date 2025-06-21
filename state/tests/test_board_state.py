import pytest

from   board                    import Coin
from   board.layout             import LayoutInterface
from   geometry                 import Point
from   state                    import BoardState


class DummyBoard(LayoutInterface):
    def __init__(self, n=2):
        self.n = 2
        self.valid_points = {Point(x, y) for x in range(3) for y in range(3)}

    @property
    def directions(self):
        return [Point(1, 0), Point(0, 1), Point(-1, 0), Point(0, -1)]

    def positive_direction(self, region: int) -> Point:
        return Point(-0, -1) if region == 1 else Point(0, 1)

    def __contains__(self, point: Point):
        return point in self.valid_points

    def __iter__(self):
        return iter(self.valid_points)

    def can_enter(self, coin, point, jump_move=False):
        return point in self.valid_points

    def is_valid_coin(self, coin: Coin):
        return coin.point in self

    def region(self, point):
        if point.x in [0, 1]:
            return point.x
        return 2

    def opposite_region(self, region: int):
        return region % 2 + 1


@pytest.fixture
def set_up():
    board = DummyBoard()
    coins = [Coin(Point(0, 0), 1), Coin(Point(1, 1), 2)]
    return BoardState(board, coins), coins


def test_initial_coin_placement(set_up):
    state, coins = set_up
    assert state.has_coin(Point(0, 0))
    state.get_coin(Point(1, 1)).region == 2  # type: ignore


def test_move_coin(set_up):
    state, coins = set_up
    state.move_coin(Point(0, 0), Point(2, 2))
    assert not state.has_coin(Point(0, 0))
    assert state.has_coin(Point(2, 2))
    assert state.get_coin(Point(2, 2)).region == 1  # type: ignore


def test_remove_coin(set_up):
    state, coins = set_up
    removed = state.remove_coin_at(Point(1, 1))
    assert removed.region == 2
    assert not state.has_coin(Point(1, 1))


def test_get_all_points_and_coins(set_up):
    state, expected_coins = set_up
    points = state.get_all_points()
    coins = state.get_all_coins()
    assert Point(0, 0) in points
    assert coins == expected_coins


def test_valid_moves_includes_adjacent(set_up):
    state, coins = set_up
    coin = state.get_coin(Point(0, 0))
    moves = state.valid_moves(coin)  # type: ignore
    assert Point(1, 0) in moves
    assert Point(0, 1) in moves


def test_steps(set_up):
    state, coins = set_up
    coin = state.get_coin(Point(0, 0))
    state.valid_moves(coin)  # type: ignore
    for dest in state.valid_moves(coin):  # type: ignore
        path = state.steps(coin, dest)
        assert path[0] == Point(0, 0)
        assert path[-1] == dest

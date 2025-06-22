import pytest

from   board                    import Coin
from   board.layout             import LayoutInterface
from   geometry                 import Point
from   state.board_state        import BoardState


class DummyBoard(LayoutInterface):
    """
    Minimal board implementation for testing.
    Implements the necessary interface expected by BoardState and AI players.
    """

    def __init__(self, coins=None):
        self._coins = coins or []
        # For __iter__ and __contains__, let's define a simple 2x2 grid
        self._points = [Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1)]

    def get_all_coins(self):
        return self._coins

    def positive_direction(self, region: int) -> Point:
        return Point(1, 1)

    @property
    def directions(self) -> list[Point]:
        return [Point(1, 0), Point(0, 1)]

    def can_enter(self, coin: Coin, point: Point, is_jump: bool = False) -> bool:
        return point.x >= 0 and point.y >= 0

    def valid_moves(self, coin):
        # For testing: allow each coin to move to two adjacent points
        return [
            Point(coin.point.x + 1, coin.point.y),
            Point(coin.point.x, coin.point.y + 1),
        ]

    def is_valid_coin(self, coin: Coin) -> bool:
        return self.can_enter(coin, coin.point)

    def region(self, point):
        # For testing: region is 1 if x is even, 2 if x is odd
        return 1 if point.x % 2 == 0 else 2

    @property
    def corners(self):
        # Provide two corners for source/destination logic
        return [Point(0, 0), Point(1, 1)]

    def opposite_region(self, region):
        # For testing: just flip between 1 and 2
        return 2 if region == 1 else 1

    def __contains__(self, point):
        # Allow only points in our simple grid
        return point in self._points

    def __iter__(self):
        # Iterate over all points in our simple grid
        return iter(self._points)


@pytest.fixture
def dummy_board_and_coins():
    coins = [Coin(Point(0, 0), 1), Coin(Point(1, 1), 2)]
    board = DummyBoard(coins)
    return board, coins


def test_get_all_coins(dummy_board_and_coins):
    board, coins = dummy_board_and_coins
    assert board.get_all_coins() == coins


def test_valid_moves(dummy_board_and_coins):
    board, coins = dummy_board_and_coins
    moves = board.valid_moves(coins[0])
    assert Point(1, 0) in moves
    assert Point(0, 1) in moves


def test_region(dummy_board_and_coins):
    board, _ = dummy_board_and_coins
    assert board.region(Point(0, 0)) == 1
    assert board.region(Point(1, 0)) == 2


def test_corners(dummy_board_and_coins):
    board, _ = dummy_board_and_coins
    corners = board.corners
    assert Point(0, 0) in corners
    assert Point(1, 1) in corners


def test_opposite_region(dummy_board_and_coins):
    board, _ = dummy_board_and_coins
    assert board.opposite_region(1) == 2
    assert board.opposite_region(2) == 1


def test_contains(dummy_board_and_coins):
    board, _ = dummy_board_and_coins
    assert Point(0, 0) in board
    assert Point(2, 2) not in board


def test_iter(dummy_board_and_coins):
    board, _ = dummy_board_and_coins
    points = list(board)
    assert Point(0, 0) in points
    assert Point(1, 0) in points
    assert Point(0, 1) in points
    assert Point(1, 1) in points


def test_board_state_integration(dummy_board_and_coins):
    board, coins = dummy_board_and_coins
    board_state = BoardState(board, coins)
    # BoardState should expose the coins and allow access to the board
    assert set(board_state.get_all_coins()) == set(coins)
    for coin in coins:
        assert coin.point in board_state.board


import pytest

from   board                    import Coin
from   geometry                 import Point
from   player                   import GreedyPlayer, MinMaxPlayer
from   state                    import BoardState, GameState
from   state.tests.test_board_state \
                                import DummyBoard


class DummyGameManager:
    def __init__(self, game_state, players=None):
        self.game_state = game_state
        self.players = players or game_state.players

    def __getattr__(self, name):
        return getattr(self.game_state, name)


@pytest.fixture
def dummy_game_manager():
    coins = [Coin(Point(0, 0), 1), Coin(Point(1, 1), 2)]
    board = DummyBoard(coins)
    board_state = BoardState(board, coins)
    players = [GreedyPlayer(0), GreedyPlayer(1)]
    player_id_region_map = {0: [1], 1: [2]}
    game_state = GameState(board_state, players, player_id_region_map)
    return DummyGameManager(game_state, players)


def test_greedy_player_compute_move(dummy_game_manager):
    player = GreedyPlayer(0)
    coin, dst = player.compute_move(dummy_game_manager)
    assert isinstance(coin, Coin)
    assert isinstance(dst, Point)
    assert dst in [Point(1, 0), Point(0, 1)]


def test_minmax_player_compute_move(dummy_game_manager):
    player = MinMaxPlayer(0, depth=1)
    coin, dst = player.compute_move(dummy_game_manager)
    assert isinstance(coin, Coin)
    assert isinstance(dst, Point)
    assert dst in [Point(1, 0), Point(0, 1)]

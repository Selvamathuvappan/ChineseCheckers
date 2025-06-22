import pytest

from   board                    import Coin
from   geometry                 import Point
from   player                   import GreedyPlayer
from   player.minmax.state      import GameStateWrapper, Move
from   state                    import BoardState, GameState
from   state.tests.test_board_state \
                                import DummyBoard


@pytest.fixture
def dummy_game_state():
    coins = [Coin(Point(0, 0), 1), Coin(Point(1, 1), 2)]
    board = DummyBoard(coins)
    board_state = BoardState(board, coins)
    players = [GreedyPlayer(0), GreedyPlayer(1)]
    player_id_region_map = {0: [1], 1: [2]}
    return GameState(board_state, players, player_id_region_map)


@pytest.fixture
def wrapper(dummy_game_state):
    return GameStateWrapper(dummy_game_state, dummy_game_state.players[0])


def test_current_player(wrapper):
    assert wrapper.current_player().player_id == 0


def test_get_legal_moves_for_coin(wrapper):
    coin = wrapper.game.get_all_coins()[0]
    moves = wrapper.get_legal_moves_for_coin(coin)
    assert all(isinstance(m[0], Move) for m in moves)
    assert all(isinstance(m[1], tuple) and len(m[1]) == 2 for m in moves)


def test_get_legal_moves(wrapper):
    moves = wrapper.get_legal_moves()
    assert all(isinstance(m, Move) for m in moves)
    assert len(moves) > 0


def test_apply_move(wrapper):
    moves = wrapper.get_legal_moves()
    new_state = wrapper.apply_move(moves[0])
    assert isinstance(new_state, GameStateWrapper)
    assert new_state.game.current_player_index != wrapper.game.current_player_index


def test_get_destination_and_source(wrapper):
    coin = wrapper.game.get_all_coins()[0]
    dest = wrapper.get_destination(coin)
    src = wrapper.get_source(coin)
    assert isinstance(dest, Point)
    assert isinstance(src, Point)


def test_isolated_coin_penalty(wrapper):
    coin = wrapper.game.get_all_coins()[0]
    penalty = wrapper.isolated_coin_penalty(coin)
    assert isinstance(penalty, (int, float))


def test_evaluate(wrapper):
    score = wrapper.evaluate()
    assert isinstance(score, (int, float))

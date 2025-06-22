import pytest

from   board                    import Coin
from   geometry                 import Point
from   player                   import GreedyPlayer
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


def test_current_player(dummy_game_state):
    assert dummy_game_state.current_player().player_id == 0


def test_next_turn(dummy_game_state):
    dummy_game_state.next_turn()
    assert dummy_game_state.current_player().player_id == 1
    dummy_game_state.next_turn()
    assert dummy_game_state.current_player().player_id == 0


def test_get_all_coins(dummy_game_state):
    coins = dummy_game_state.get_all_coins()
    assert all(isinstance(c, Coin) for c in coins)
    assert len(coins) == 2


def test_is_players_coin(dummy_game_state):
    coin0, coin1 = dummy_game_state.get_all_coins()
    assert dummy_game_state.is_players_coin(coin0, dummy_game_state.players[0])
    assert not dummy_game_state.is_players_coin(coin1, dummy_game_state.players[0])
    assert dummy_game_state.is_players_coin(coin1, dummy_game_state.players[1])


def test_valid_moves(dummy_game_state):
    coin = dummy_game_state.get_all_coins()[0]
    moves = dummy_game_state.valid_moves(coin)
    assert Point(1, 0) in moves


def test_has_current_player_won(dummy_game_state):
    # Simulate all coins in opposite region for player 0
    for coin in dummy_game_state.get_all_coins():
        coin.region = 2
    assert dummy_game_state.has_current_player_won()
    # Not all coins in opposite region
    dummy_game_state.get_all_coins()[0].region = 1
    assert not dummy_game_state.has_current_player_won()


def test_player_id_region_map(dummy_game_state):
    assert dummy_game_state.player_id_region_map[0] == [1]
    assert dummy_game_state.player_id_region_map[1] == [2]

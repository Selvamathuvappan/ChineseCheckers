from typing import Optional

import pytest

from board.coin import Coin
from geometry import Point
from player.base import Player
from state.board_state import BoardState
from state.game_state import GameState
from state.tests.test_board_state import DummyBoard


class DummyPlayer(Player):
    def perform_turn(self, game, io) -> None:
        pass

@pytest.fixture
def game_state_factory():
    def _factory(coins, player_id_region_map, players: Optional[list[Player]]=None, board=None):
        if players is None:
            players = [DummyPlayer(pid) for pid in player_id_region_map]
        if board is None:
            board = BoardState(DummyBoard(), coins)
        return GameState(board, players, player_id_region_map)
    return _factory

def test_is_players_coin(game_state_factory):
    coins = [Coin(Point(0, 0), region=1), Coin(Point(1, 0), region=2)]
    player_id_region_map = {0: [1], 1: [2]}
    gs = game_state_factory(coins, player_id_region_map)
    assert gs.is_players_coin(coins[0], gs.players[0])
    assert not gs.is_players_coin(coins[1], gs.players[0])
    assert gs.is_players_coin(coins[1], gs.players[1])

def test_has_current_player_won(game_state_factory):
    coins = [Coin(Point(0, 1), region=1), Coin(Point(1, 0), region=2)]
    player_id_region_map = {0: [1], 1: [2]}
    gs = game_state_factory(coins, player_id_region_map)
    gs.current_player_index = 0
    assert not gs.has_current_player_won()
    coins[0] = Coin(Point(2, 1), region=1)
    gs = game_state_factory(coins, player_id_region_map)
    assert gs.has_current_player_won()

def test_turn_cycling(game_state_factory):
    coins = []
    player_id_region_map = {0: [1], 1: [2], 2: [3]}
    gs = game_state_factory(coins, player_id_region_map)
    assert gs.current_player_index == 0
    gs.next_turn()
    assert gs.current_player_index == 1
    gs.next_turn()
    assert gs.current_player_index == 2
    gs.next_turn()
    assert gs.current_player_index == 0

def test_getattr_delegation(game_state_factory):
    coins = []
    player_id_region_map = {0: [1]}
    gs = game_state_factory(coins, player_id_region_map)
    # Should delegate to board
    assert hasattr(gs, "get_all_points")

def test_players_coin_with_central_region(game_state_factory):
    coins = [Coin(Point(0, 1), region=1)]
    player_id_region_map = {0: [1], 1: [2]}
    gs = game_state_factory(coins, player_id_region_map)
    assert gs.is_players_coin(coins[0], gs.players[0])
    assert not gs.is_players_coin(coins[0], gs.players[1])
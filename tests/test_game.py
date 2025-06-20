import pytest

from   board.coin               import Coin
from   game                     import GameManager
from   geometry.point           import Point
from   render.board             import BaseBoardRenderer
from   state.board_state        import BoardState
from   state.tests.test_board_state \
                                import DummyBoard


class DummyMutator(BoardState):
    def __init__(self, coins):
        self.board = DummyBoard()
        self._coins = coins

    def get_all_coins(self):
        return self._coins


class DummyRenderer(BaseBoardRenderer):
    def __init__(self, coins):
        self.mutator = DummyMutator(coins)

    def render(self):
        pass

    def prompt_player(self, player, regions):
        pass

    def prompt_win(self, player, regions):
        pass


def test_initialization():
    renderer = DummyRenderer([])
    manager = GameManager(renderer, num_players=1, regions_per_player=1)
    assert manager.current_player() == 0
    assert len(manager.player_region_map) == 1
    assert isinstance(manager.player_region_map[0], list)


def test_region_assignment_validation():
    renderer = DummyRenderer([])
    with pytest.raises(ValueError):
        GameManager(
            renderer, num_players=3, regions_per_player=1
        )  # 4 regions needed, only 3 exist


def test_turn_cycling():
    renderer = DummyRenderer([])
    manager = GameManager(renderer, num_players=2, regions_per_player=1)
    assert manager.current_player() == 0
    manager.next_turn()
    assert manager.current_player() == 1
    manager.next_turn()
    assert manager.current_player() == 0
    manager.next_turn()
    assert manager.current_player() == 1


def test_is_players_coin():
    coin_owned = Coin(Point(0, 0), region=1)
    coin_other = Coin(Point(1, 0), region=2)
    renderer = DummyRenderer([coin_owned, coin_other])
    manager = GameManager(renderer, num_players=1, regions_per_player=1)
    assert manager.is_players_coin(coin_owned)
    assert not manager.is_players_coin(coin_other)


def test_has_current_player_won():
    # player 0 has all coins in opposite region (region 1)
    coins = [
        Coin(Point(0, 0), region=2),
        Coin(Point(-1, 0), region=1),
    ]
    renderer = DummyRenderer(coins)
    manager = GameManager(renderer, num_players=1, regions_per_player=1)
    assert manager.has_current_player_won()

    # Fix coin region
    coins[1] = Coin(Point(1, 0), region=1)
    renderer = DummyRenderer(coins)
    manager = GameManager(renderer, num_players=1, regions_per_player=1)
    assert not manager.has_current_player_won()

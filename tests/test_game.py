import pytest

from   board.coin               import Coin
from   game                     import GameManager
from   geometry                 import Point
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
        self.prompt_player_called = False
        self.prompt_win_called = False
        self.screen_to_board_called = False

    def render(self, *args, **kwargs):
        pass

    def prompt_player(self, player, regions):
        self.prompt_player_called = True

    def prompt_win(self, player, regions):
        self.prompt_win_called = True

    def screen_to_board(self, board: BoardState, point: Point) -> Point:
        self.screen_to_board_called = True
        return point


@pytest.fixture
def game_manager_factory():
    def _factory(total_colors=6, num_players=(1, 0), colors_per_player=1):
        renderer = DummyRenderer([])
        return GameManager(
            renderer=renderer,
            total_colors=total_colors,
            num_players=num_players,
            colors_per_player=colors_per_player,
        )

    return _factory


def test_initialization(game_manager_factory):
    num_players = (2, 0)
    manager = game_manager_factory(num_players=num_players)
    assert manager.current_player_index == 0
    assert isinstance(manager.player_id_region_map, dict)
    assert len(manager.players) == sum(num_players)


def test_region_assignment_validation(game_manager_factory):
    with pytest.raises(ValueError):
        game_manager_factory(total_colors=3, num_players=(2, 2), colors_per_player=1)


def test_turn_cycling(game_manager_factory):
    manager = game_manager_factory(num_players=(2, 0))
    assert manager.current_player_index == 0
    manager.next_turn()
    assert manager.current_player_index == 1
    manager.next_turn()
    assert manager.current_player_index == 0


def test_multiple_players_multiple_regions(game_manager_factory):
    manager = game_manager_factory(num_players=(3, 0))
    assert manager.current_player_index == 0
    manager.next_turn()
    assert manager.current_player_index == 1
    manager.next_turn()
    assert manager.current_player_index == 2
    manager.next_turn()
    assert manager.current_player_index == 0


def test_getattr_delegation(game_manager_factory):
    manager = game_manager_factory()
    # Should delegate to game_state
    assert hasattr(manager, "current_player")


def test_prompt_player_and_win_calls_renderer(game_manager_factory):
    manager = game_manager_factory()
    manager.prompt_player()
    assert manager.renderer.prompt_player_called
    manager.prompt_win()
    assert manager.renderer.prompt_win_called


def test_too_many_regions_per_player(game_manager_factory):
    with pytest.raises(ValueError):
        game_manager_factory(total_colors=6, num_players=(2, 0), colors_per_player=10)


def test_is_players_coin_multiple_players(game_manager_factory):
    coins = [
        Coin(Point(0, 0), region=1),
        Coin(Point(2, 0), region=4),
    ]
    manager = game_manager_factory(num_players=(2, 0))
    assert manager.is_players_coin(coins[0], player=manager.players[0])
    assert manager.is_players_coin(coins[1], player=manager.players[1])
    assert not manager.is_players_coin(coins[0], player=manager.players[1])
    assert not manager.is_players_coin(coins[1], player=manager.players[0])

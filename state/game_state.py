from   typing                   import Any, Optional, TYPE_CHECKING

from   board                    import Coin

if TYPE_CHECKING:
    from player.base import Player
    from state.board_state import BoardState


class GameState:
    """
    Controls the overall game flow, including player turns, region
    assignments, and win detection.
    """

    def __init__(
        self,
        board_state: "BoardState",
        players: list["Player"],
        player_id_region_map: dict[int, list[int]],
    ) -> None:
        """
        Initializes the GameState with the game setup.
        """
        self.players = players
        self.player_id_region_map = player_id_region_map
        self.board = board_state
        self.current_player_index = 0

    def __getattr__(self, name) -> Any:
        """
        Delegate attribute access to the board if not found in GameState.
        """
        return getattr(self.board, name)

    def current_player(self) -> "Player":
        """Returns the the current player."""
        return self.players[self.current_player_index]

    def is_players_coin(self, coin: Coin, player: Optional["Player"] = None) -> bool:
        """
        Checks if the given coin belongs to the current player.
        """
        player = player or self.current_player()
        return coin.region in self.player_id_region_map[player.player_id]

    def next_turn(self) -> None:
        """Advances the turn to the next player."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def has_current_player_won(self) -> bool:
        """
        Checks whether the current player has won.
        A player wins if all their coins are in the opposite region.
        """
        player_id = self.current_player().player_id
        return all(
            self.board.coin_at_destination(coin)
            for coin in self.board.get_all_coins()
            if coin.region in self.player_id_region_map[player_id]
        )

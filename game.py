from   typing                   import Any

from   board                    import Coin, Layout
from   player                   import GreedyPlayer, HumanPlayer
from   player.base              import Player
from   render.board             import BaseBoardRenderer
from   state                    import GameState
from   state.board_state        import BoardState
from   utils                    import get_spaced_around_spots


class GameManager:
    """
    Controls the overall game flow, including player turns, region
    assignments, and win detection.

    Attributes:
        renderer (BaseBoardRenderer): Responsible for rendering board state.
        players (List[Player]): List of player identifiers.
        player_id_region_map (Dict[int, List[int]]): Maps each player to their regions.
        current_player_index (int): Tracks whose turn it is.
    """

    def __init__(
        self,
        renderer: BaseBoardRenderer,
        total_colors: int,
        num_players: tuple[int, int],
        colors_per_player: int,
    ) -> None:
        """
        Initializes the GameManager with the game setup.

        Args:
            renderer (CursesBoardRenderer): Renderer instance managing board visuals and state.
            num_players (tuple[int, int]): Total number of (human players, computer player).
            colors_per_player (int): Number of regions each player controls.

        Raises:
            ValueError: If total regions requested exceed the number available on the board.
        """
        human_players, computer_players = num_players
        total_players = sum(num_players)
        players: list[Player] = [
            *[HumanPlayer(i) for i in range(human_players)],
            *[GreedyPlayer(i) for i in range(human_players, total_players)],
        ]
        if colors_per_player * total_players > total_colors:
            raise ValueError("Too many regions requested for given number of players.")
        regions_range_per_player = total_colors // total_players
        player_id_region_map: dict[int, list[int]] = self._generate_region_map(
            players, regions_range_per_player, colors_per_player, total_colors
        )
        all_regions = sum(player_id_region_map.values(), [])
        layout = Layout(side_count=total_colors)
        coins = [
            Coin(point, region)
            for point in layout
            if (region := layout.region(point))
            if region in all_regions
        ]
        self.game_state = GameState(
            BoardState(layout, coins),
            players,
            player_id_region_map,
        )
        self.renderer = renderer

    def __getattr__(self, name) -> Any:
        return getattr(self.game_state, name)

    @staticmethod
    def _generate_region_map(
        players, regions_range_per_player, colors_per_player, total_colors
    ) -> dict[int, list[int]]:
        """
        Creates a mapping of each player to a list of region indices.

        Args:
            regions_range_per_player (int): Size of region range per player.
            colors_per_player (int): Number of regions per player.
            total_colors (int): Total number of regions on the board.

        Returns:
            Dict[int, List[int]]: Mapping of player to region indices.
        """
        return {
            player.player_id: [
                (pos + idx * regions_range_per_player) % total_colors + 1
                for pos in get_spaced_around_spots(
                    regions_range_per_player, colors_per_player, total_colors
                )
            ]
            for idx, player in enumerate(players)
        }

    def prompt_player(self) -> None:
        """
        Displays a prompt indicating the current player's turn.
        """
        player = self.game_state.current_player()
        self.renderer.prompt_player(
            player, self.game_state.player_id_region_map[player.player_id]
        )

    def prompt_win(self) -> None:
        """
        Displays a prompt indicating the winner.
        """
        player = self.game_state.current_player()
        self.renderer.prompt_win(
            player, self.game_state.player_id_region_map[player.player_id]
        )

from   functools                import partial
from   typing                   import Optional

from   board                    import Layout
from   board.coin               import Coin
from   player.base              import Player
from   player.computer          import ComputerPlayer
from   player.human             import HumanPlayer
from   render.board             import BaseBoardRenderer
from   utils                    import get_spaced_around_spots


class GameManager:
    """
    Controls the overall game flow, including player turns, region
    assignments, and win detection.

    Attributes:
        renderer (BaseBoardRenderer): Responsible for rendering board state.
        players (List[Player]): List of player identifiers.
        player_region_map (Dict[int, List[int]]): Maps each player to their regions.
        current_player_index (int): Tracks whose turn it is.
    """

    def __init__(
        self,
        renderer_factory: partial[BaseBoardRenderer],
        total_colors,
        num_players: tuple[int, int],
        colors_per_player,
    ):
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
        self.players = [HumanPlayer(i) for i in range(human_players)] + [
            ComputerPlayer(i) for i in range(human_players, total_players)
        ]
        if colors_per_player * total_players > total_colors:
            raise ValueError("Too many regions requested for given number of players.")
        regions_range_per_player = total_colors // total_players
        self.player_region_map: dict[int, list[int]] = self._generate_region_map(
            regions_range_per_player, colors_per_player, total_colors
        )
        all_regions = sum(self.player_region_map.values(), [])
        layout = Layout(side_count=total_colors)
        coins = [
            Coin(point, region)
            for point in layout
            if (region := layout.region(point)) in all_regions
        ]
        self.current_player_index = 0
        self.renderer = renderer_factory(board=layout, coins=coins)

    def _generate_region_map(
        self, regions_range_per_player, colors_per_player, total_colors
    ):
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
            for idx, player in enumerate(self.players)
        }

    def current_player(self) -> Player:
        """Returns the ID of the current player."""
        return self.players[self.current_player_index]

    def prompt_player(self):
        """
        Displays a prompt indicating the current player's turn.
        """
        player = self.current_player()
        self.renderer.prompt_player(player, self.player_region_map[player.player_id])

    def prompt_win(self):
        """
        Displays a prompt indicating the winner.
        """
        player = self.current_player()
        self.renderer.prompt_win(player, self.player_region_map[player.player_id])

    def is_players_coin(self, coin: Coin, player: Optional[Player] = None):
        """
        Checks if the given coin belongs to the current player.

        Args:
            coin (Coin): The coin to check.

        Returns:
            bool: True if the coin belongs to the current player.
        """
        player = player or self.current_player()
        return coin.region in self.player_region_map[player.player_id]

    def next_turn(self):
        """Advances the turn to the next player."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def has_current_player_won(self):
        """
        Checks whether the current player has won.

        A player wins if all their coins are in the opposite region.

        Returns:
            bool: True if the current player has won.
        """
        player_id = self.current_player().player_id
        return all(
            self.renderer.mutator.coin_at_destination(coin)
            for coin in self.renderer.mutator.get_all_coins()
            if coin.region in self.player_region_map[player_id]
        )

from   abc                      import ABC, abstractmethod
import curses
import logging
import time
from   typing                   import Iterable, List, Optional, TYPE_CHECKING

from   board                    import Coin
from   board.layout             import LayoutInterface
from   geometry                 import Point

if TYPE_CHECKING:
    from player.base import Player

from   render.color_manager     import color_manager
from   render.exceptions        import SmallScreenError
from   state                    import BoardState

logger = logging.getLogger(__name__)


class BaseBoardRenderer(ABC):
    """
    Abstract base class for rendering a Chinese Checkers board.
    Handles the logical structure of mutating and rendering board state.
    Concrete subclasses should implement the actual render logic.
    """

    def __init__(
        self,
        board: LayoutInterface,
        coins: Iterable[Coin],
        points_to_highlight: Optional[set[Point]] = None,
        frame_delay: float = 0.2,
    ):
        assert all(board.is_valid_coin(coin) for coin in coins)
        self.mutator = BoardState(board, coins)
        self.points_to_highlight: set[Point] = points_to_highlight or set()
        self.delay = frame_delay

    @abstractmethod
    def render(self):
        """
        Render the entire board.
        Must be implemented by subclasses.
        """
        pass

    def highlight(self, points: set[Point]):
        """
        Highlight a given set of points.

        Args:
            points (set[Point]): Points to highlight on the board.
        """
        self.points_to_highlight = points

    def move(self, moves: List[Point]):
        """
        Animate a sequence of moves.

        Args:
            moves (List[Point]): A list of points representing a path.
        """
        self.highlight({moves[0]})
        self.render()
        time.sleep(self.delay)
        for point, nxt_point in zip(moves, moves[1:]):
            self.mutator.move_coin(point, nxt_point)
            self.highlight({nxt_point})
            self.render()
            time.sleep(self.delay)
        self.highlight(set())
        self.render()

    @abstractmethod
    def screen_to_board(self, point) -> Point:
        """Converts screen coordinate back to board coordinate."""
        pass

    @abstractmethod
    def prompt_player(self, player, regions):
        pass

    @abstractmethod
    def prompt_win(self, player, regions):
        pass


class CursesBoardRenderer(BaseBoardRenderer):
    """
    Handles rendering of the board and coins in a curses-based terminal UI.
    Coordinates rendering logic, coin state mutation, and visual highlighting.
    """

    def __init__(
        self,
        stdscr,
        board: LayoutInterface,
        coins: Iterable[Coin],
        points_to_highlight=None,
        frame_delay=0.2,
    ):
        self.stdscr = stdscr
        super().__init__(board, coins, points_to_highlight, frame_delay)
        self.offset = self.compute_offset()

    def render(self):
        """Renders the board with coins and highlighted points."""
        points = self.mutator.get_all_points()
        logger.debug(f"rendering {len(points)} points")
        transformed_points = list(map(self.board_to_screen, points))
        for orig_point, display_point in zip(points, transformed_points):
            region = getattr(self.mutator.get_coin(orig_point), "region", 0)
            highlight = orig_point in self.points_to_highlight
            self.render_point(
                display_point,
                region,
                highlight,
            )
        self.stdscr.refresh()

    def compute_offset(self):
        """
        Computes offset to center the board on screen.

        Returns:
            Point: Offset to apply to all board points.

        Raises:
            SmallScreenError: If screen is too small to render the board.
        """
        max_y, max_x = self.stdscr.getmaxyx()
        points = [Point(x, -y) for x, y in self.mutator.get_all_points()]

        min_x = min(x for x, y in points)
        min_y = min(y for x, y in points)
        points = [(x - min_x, y - min_y) for x, y in points]

        width = max(x for x, y in points) + 1
        height = max(y for x, y in points) + 1

        if width > max_x or height > max_y:
            raise SmallScreenError

        offset_x = (max_x - width) // 2
        offset_y = (max_y - height) // 2
        return Point(offset_x - min_x, offset_y - min_y)

    def board_to_screen(self, point: Point):
        """Converts board coordinate to screen coordinate."""
        x, y = point
        return Point(x, -y) + self.offset

    def screen_to_board(self, point: Point):
        """Converts screen coordinate back to board coordinate."""
        x, y = point - self.offset
        return Point(x, -y)

    def render_point(self, point: Point, region: int, highlight=False):
        """
        Renders a single point on the screen.

        Args:
            point (Point): Location on the screen.
            region (int): Region ID of the coin.
            highlight (bool): Whether to highlight this point.
        """
        attr = color_manager(region, highlight)
        self.stdscr.addstr(point.y, point.x, "●", attr)

    def prompt_helper(
        self, position, player: "Player", regions: Iterable[int], prompt: str
    ):
        self.stdscr.move(*position)
        self.stdscr.clrtoeol()

        self.stdscr.addstr("Player ", curses.A_BOLD)

        for region in regions:
            attr = color_manager(region)
            self.stdscr.addstr("●", attr)

        self.stdscr.addstr(prompt.format(player=player.player_id))

    def prompt_player(self, player: "Player", regions: Iterable[int]):
        self.prompt_helper(
            (0, 0), player, regions, " (Player {player})'s turn. Press 'q' to quit."
        )

    def prompt_win(self, player, regions):
        self.prompt_helper(
            (0, 0), player, regions, " (Player {player}) wins! Press any key to exit."
        )

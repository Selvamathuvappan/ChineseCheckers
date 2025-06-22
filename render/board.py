from   abc                      import ABC, abstractmethod
import curses
import logging
import time
from   typing                   import Iterable, List, Optional, TYPE_CHECKING

from   geometry                 import Point
from   render.color_manager     import color_manager
from   render.exceptions        import SmallScreenError
from   state                    import BoardState

if TYPE_CHECKING:
    from player.base import Player

logger = logging.getLogger(__name__)


class BaseBoardRenderer(ABC):
    """
    Abstract base class for rendering a Chinese Checkers board.
    Handles the logical structure of mutating and rendering board state.
    Concrete subclasses should implement the actual render logic.
    """

    def __init__(
        self,
        points_to_highlight: Optional[set[Point]] = None,
        frame_delay: float = 0.2,
    ) -> None:
        self.points_to_highlight: set[Point] = points_to_highlight or set()
        self.delay = frame_delay

    @abstractmethod
    def render(self, board: BoardState) -> None:
        """
        Render the entire board.
        Must be implemented by subclasses.
        """
        pass

    def highlight(self, board: BoardState, points: set[Point]) -> None:
        """Highlight a given set of points on the board."""
        self.points_to_highlight = points
        self.render(board)

    def move(self, board: BoardState, moves: List[Point]) -> None:
        """Animate a sequence of moves."""
        self.highlight(board, {moves[0]})
        time.sleep(self.delay)
        for point, nxt_point in zip(moves, moves[1:]):
            board.move_coin(point, nxt_point)
            self.highlight(board, {nxt_point})
            time.sleep(self.delay)
        self.highlight(board, set())

    @abstractmethod
    def screen_to_board(self, board: BoardState, point: Point) -> Point:
        """Converts screen coordinate back to board coordinate."""
        pass

    @abstractmethod
    def prompt_player(self, player: "Player", regions: Iterable[int]) -> None:
        pass

    @abstractmethod
    def prompt_win(self, player: "Player", regions: Iterable[int]) -> None:
        pass


class CursesBoardRenderer(BaseBoardRenderer):
    """
    Handles rendering of the board and coins in a curses-based terminal UI.
    Coordinates rendering logic, coin state mutation, and visual highlighting.
    """

    def __init__(
        self,
        stdscr,
        points_to_highlight: Optional[set[Point]] = None,
        frame_delay: float = 0.2,
    ) -> None:
        self.stdscr = stdscr
        self.board_offset_map: dict[BoardState, Point] = {}
        super().__init__(points_to_highlight, frame_delay)

    def render(self, board: BoardState) -> None:
        """Renders the board with coins and highlighted points."""
        points = board.get_all_points()
        transformed_points = list(
            map((lambda point: self.board_to_screen(board, point)), points)
        )
        for orig_point, display_point in zip(points, transformed_points):
            region = getattr(board.get_coin(orig_point), "region", 0)
            highlight = orig_point in self.points_to_highlight
            self.render_point(
                display_point,
                region,
                highlight,
            )
        self.stdscr.refresh()

    def offset(self, board: BoardState) -> Point:
        """
        Computes offset to center the board on screen.

        Returns:
            Point: Offset to apply to all board points.

        Raises:
            SmallScreenError: If screen is too small to render the board.
        """
        if board not in self.board_offset_map:
            max_y, max_x = self.stdscr.getmaxyx()
            points = [Point(x, -y) for x, y in board.get_all_points()]

            min_x = min(x for x, y in points)
            min_y = min(y for x, y in points)
            points = [(x - min_x, y - min_y) for x, y in points]

            width = max(x for x, y in points) + 1
            height = max(y for x, y in points) + 1

            if width > max_x or height > max_y:
                raise SmallScreenError

            offset_x = (max_x - width) // 2
            offset_y = (max_y - height) // 2
            self.board_offset_map[board] = Point(offset_x - min_x, offset_y - min_y)
        return self.board_offset_map[board]

    def board_to_screen(self, board: BoardState, point: Point) -> Point:
        """Converts board coordinate to screen coordinate."""
        x, y = point
        return Point(x, -y) + self.offset(board)

    def screen_to_board(self, board: BoardState, point: Point) -> Point:
        """Converts screen coordinate back to board coordinate."""
        x, y = point - self.offset(board)
        return Point(x, -y)

    def render_point(self, point: Point, region: int, highlight=False) -> None:
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
    ) -> None:
        self.stdscr.move(*position)
        self.stdscr.clrtoeol()
        from player.human import HumanPlayer

        player_prefix = "Human" if isinstance(player, HumanPlayer) else "Computer"

        self.stdscr.addstr(f"{player_prefix} Player ", curses.A_BOLD)

        for region in regions:
            attr = color_manager(region)
            self.stdscr.addstr("●", attr)

        self.stdscr.addstr(prompt.format(player=player.player_id))

    def prompt_player(self, player: "Player", regions: Iterable[int]) -> None:
        self.prompt_helper(
            (0, 0), player, regions, " (Player {player})'s turn. Press 'q' to quit."
        )

    def prompt_win(self, player: "Player", regions: Iterable[int]) -> None:
        self.prompt_helper(
            (0, 0), player, regions, " (Player {player}) wins! Press any key to exit."
        )

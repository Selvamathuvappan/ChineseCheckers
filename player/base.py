from   abc                      import ABC, abstractmethod
import curses
from   typing                   import Any, TYPE_CHECKING

from   geometry                 import Point
from   render.exceptions        import ExitGame

if TYPE_CHECKING:
    from game import GameManager


class IOInterface(ABC):
    """
    Abstract base class for user input/output handling.
    """

    def __init__(self) -> None:
        self._should_quit = False

    @abstractmethod
    def get_mouse_point(self) -> Point:
        """Returns the current mouse position as a Point."""
        pass

    @abstractmethod
    def wait_till_input(self) -> Any:
        """Waits for and returns the next user input."""
        pass

    @abstractmethod
    def peek_key(self) -> None:
        """Peeks at the next key input without blocking."""
        pass

    def quit_requested(self) -> bool:
        """Returns True if the user has requested to quit."""
        return self._should_quit

    @abstractmethod
    def should_handle_move(self, key) -> bool:
        """Determines if current (human) player is ready to handle a move."""
        pass


class Player(ABC):
    """
    Abstract base class for a player in the game.
    """

    def __init__(self, player_id: int) -> None:
        self._player_id = player_id

    @property
    def player_id(self) -> int:
        """Returns the player's unique ID."""
        return self._player_id

    @abstractmethod
    def perform_turn(self, game: "GameManager", io: IOInterface) -> None:
        """Performs a turn for the player."""
        pass

    def play_turn(self, game: "GameManager", io: IOInterface) -> None:
        """Handles pre-turn checks and delegates to perform_turn."""
        io.peek_key()
        if io.quit_requested():
            raise ExitGame("Quit requested")
        self.perform_turn(game, io)


class CursesIO(IOInterface):
    """
    Curses-based implementation of IOInterface for terminal input.
    """

    def __init__(self, stdscr) -> None:
        self.stdscr = stdscr
        super().__init__()

    def get_mouse_point(self) -> Point:
        _, mx, my, _, _ = curses.getmouse()
        return Point(mx, my)

    def wait_till_input(self):
        return self.stdscr.getch()

    def should_handle_move(self, key) -> bool:
        """Determines if current (human) player is ready to handle a move."""
        return key == curses.KEY_MOUSE

    def peek_key(self):
        self.stdscr.nodelay(True)
        try:
            key = self.stdscr.getch()
            if key == ord("q"):
                self._should_quit = True
            return key
        finally:
            self.stdscr.nodelay(False)

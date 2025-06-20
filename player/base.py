from   abc                      import ABC, abstractmethod
import curses
from   typing                   import Any, TYPE_CHECKING

from   geometry.point           import Point
from   render.exceptions        import ExitGame

if TYPE_CHECKING:
    from game import GameManager


class IOInterface(ABC):
    def __init__(self):
        self._should_quit = False

    @abstractmethod
    def get_mouse_point(self) -> Point:
        pass

    @abstractmethod
    def wait_till_input(self) -> Any:
        pass

    @abstractmethod
    def peek_key(self):
        pass

    def quit_requested(self) -> bool:
        return self._should_quit


class Player(ABC):
    def __init__(self, player_id: int):
        self._player_id = player_id

    @property
    def player_id(self):
        return self._player_id

    @abstractmethod
    def perform_turn(self, game: "GameManager", io: IOInterface):
        pass

    def play_turn(self, game: "GameManager", io: IOInterface):
        io.peek_key()
        if io.quit_requested():
            raise ExitGame("Quit requested")
        self.perform_turn(game, io)


class CursesIO(IOInterface):
    def __init__(self, stdscr):
        self.stdscr = stdscr
        super().__init__()

    def get_mouse_point(self) -> Point:
        _, mx, my, _, _ = curses.getmouse()
        return Point(mx, my)

    def wait_till_input(self):
        return self.stdscr.getch()

    def peek_key(self):
        self.stdscr.nodelay(True)
        try:
            key = self.stdscr.getch()
            if key == ord("q"):
                self._should_quit = True
            return key
        finally:
            self.stdscr.nodelay(False)

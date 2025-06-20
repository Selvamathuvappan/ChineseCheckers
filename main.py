import curses
from   functools                import partial
import logging
import os

from   board.constants          import REGION_POLYGON_MAP
from   game                     import GameManager
from   player.base              import CursesIO
from   render                   import CursesBoardRenderer
from   render.exceptions        import ExitGame, SmallScreenError

logging.basicConfig(
    filename="debug.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def prompt_game_setup():
    while True:
        try:
            total_colors = int(
                input(
                    f"Enter total number of colors (regions on board) from {', '.join(map(str, REGION_POLYGON_MAP))}: "
                )
            )
            if total_colors not in REGION_POLYGON_MAP:
                print("Please enter valid numbers.\n")
                continue
            num_players = tuple(
                map(
                    int,
                    input(
                        "Enter ',' separated number of human and computer players: "
                    ).split(","),
                )
            )
            if len(num_players) != 2:
                print("Please enter only 2 ',' separated number of players.\n")
                continue
            colors_per_player = int(input("Enter number of colors per player: "))

            if total_colors < sum(num_players) * colors_per_player:
                print(
                    "Not enough colors for all players. Please enter valid numbers.\n"
                )
                continue

            # Clear the screen before starting curses
            os.system("clear" if os.name != "nt" else "cls")
            return partial(
                GameManager,
                total_colors=total_colors,
                num_players=num_players,
                colors_per_player=colors_per_player,
            )

        except ValueError:
            print("Please enter valid integers.\n")


def main(stdscr, game_factory: partial[GameManager]):
    curses.curs_set(0)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.start_color()
    curses_io = CursesIO(stdscr)
    try:
        renderer_factory = partial(CursesBoardRenderer, stdscr=stdscr)
        game = game_factory(renderer_factory)
        game.renderer.render()

        while True:
            game.prompt_player()
            stdscr.clrtoeol()
            stdscr.refresh()

            try:
                game.current_player().play_turn(game, curses_io)
                if game.has_current_player_won():
                    game.prompt_win()
                    stdscr.getch()
                    return
                game.next_turn()

            except ExitGame:
                return
    except SmallScreenError:
        stdscr.addstr(0, 0, f"Screen too small")
        stdscr.refresh()
        stdscr.getch()
        return
    except curses.error:
        pass  # Ignore invalid click


game_factory = prompt_game_setup()
curses.wrapper(lambda stdscr: main(stdscr, game_factory))

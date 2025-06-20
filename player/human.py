import curses
from   typing                   import TYPE_CHECKING

if TYPE_CHECKING:
    from game import GameManager

from   player.base              import IOInterface, Player
from   render.exceptions        import ExitGame


class HumanPlayer(Player):
    def __init__(self, player_id):
        super().__init__(player_id)
        self.selected_coin = None
        self.highlighted_moves = set()

    def handle_move(self, game: "GameManager", io: IOInterface) -> bool:
        move_over = False
        clicked_point = game.renderer.screen_to_board(io.get_mouse_point())
        coin_at_click = game.renderer.mutator.get_coin(clicked_point)
        if self.selected_coin is None:
            if not coin_at_click:
                return False
            if game.is_players_coin(coin_at_click, self):
                self.selected_coin = coin_at_click
                self.highlighted_moves = game.renderer.mutator.valid_moves(
                    self.selected_coin
                )
        else:
            if clicked_point in self.highlighted_moves:
                move_path = game.renderer.mutator.steps(
                    self.selected_coin, clicked_point
                )
                game.renderer.move(move_path)
                move_over = True
            self.selected_coin = None
            self.highlighted_moves = set()
        game.renderer.highlight(self.highlighted_moves)
        game.renderer.render()
        return move_over

    def perform_turn(self, game: "GameManager", io: IOInterface):
        while key := io.wait_till_input():
            if key == ord("q"):
                raise ExitGame(f"Game exited by Player {self.player_id}")
            if key == curses.KEY_MOUSE:
                if self.handle_move(game, io):
                    return

from   typing                   import TYPE_CHECKING

from   player.base              import IOInterface, Player
from   render.exceptions        import ExitGame

if TYPE_CHECKING:
    from game import GameManager


class HumanPlayer(Player):
    """
    A human player that selects moves via the IO interface.
    """

    def __init__(self, player_id) -> None:
        """
        Initializes a human player.
        """
        super().__init__(player_id)
        self.selected_coin = None
        self.highlighted_moves = set()

    def handle_move(self, game: "GameManager", io: IOInterface) -> bool:
        """
        Handles a mouse click event for selecting and moving coins.
        Returns True if a move was performed, False otherwise.
        """
        move_over = False
        clicked_point = game.renderer.screen_to_board(game.board, io.get_mouse_point())
        coin_at_click = game.get_coin(clicked_point)
        if self.selected_coin is None:
            if not coin_at_click:
                return False
            if game.is_players_coin(coin_at_click, self):
                self.selected_coin = coin_at_click
                self.highlighted_moves = game.valid_moves(self.selected_coin)
        else:
            if clicked_point in self.highlighted_moves:
                move_path = game.steps(self.selected_coin, clicked_point)
                game.renderer.move(game.board, move_path)
                move_over = True
            self.selected_coin = None
            self.highlighted_moves = set()
        game.renderer.highlight(game.board, self.highlighted_moves)
        return move_over

    def perform_turn(self, game: "GameManager", io: IOInterface) -> None:
        """Waits for user input and performs a move when a valid one is made."""
        while key := io.wait_till_input():
            if key == ord("q"):
                raise ExitGame(f"Game exited by Player {self.player_id}")
            if io.should_handle_move(key):
                if self.handle_move(game, io):
                    return

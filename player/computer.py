import time
from   typing                   import Optional, TYPE_CHECKING

from   board                    import Coin
from   board.metrics            import DistanceMetrics
from   geometry                 import Point
from   player.base              import IOInterface, Player

if TYPE_CHECKING:
    from game import GameManager


class GreedyPlayer(Player):
    """
    A computer player that selects moves greedily based on distance metrics.
    """

    def evaluate(
        self, game: "GameManager", coin: Coin, dst: Point
    ) -> tuple[float, float]:
        """
        Evaluate a move for a coin to a destination using distance metrics.
        Returns a tuple for sorting preference.
        """
        valuation_engine = DistanceMetrics(game.board.board)
        return (
            valuation_engine.positive_distance(coin, dst),
            valuation_engine.distance(coin.point, dst),
        )

    def get_best_move(self, game: "GameManager", coin: Coin) -> Optional[Point]:
        """
        Returns the best move for a given coin, or None if no moves are available.
        """
        moves = game.valid_moves(coin)
        if not moves:
            return None
        return max(moves, key=lambda dst: self.evaluate(game, coin, dst))

    def compute_move(self, game: "GameManager") -> tuple[Coin, Point]:
        """
        Computes the best move for any of the player's coins.
        Returns a (coin, destination) tuple, or None if no moves are possible.
        """
        coins = [
            coin for coin in game.get_all_coins() if game.is_players_coin(coin, self)
        ]
        coin_move_map = {
            coin: move for coin in coins if (move := self.get_best_move(game, coin))
        }
        coin_to_move = max(
            coin_move_map,
            key=lambda coin: self.evaluate(game, coin, coin_move_map[coin]),
        )
        return coin_to_move, coin_move_map[coin_to_move]

    def perform_turn(self, game: "GameManager", io: IOInterface) -> None:
        """
        Performs a turn by selecting and executing the best move.
        """
        coin, dst = self.compute_move(game)
        game.renderer.highlight(game.board, {coin.point})
        move_path = game.steps(coin, dst)
        time.sleep(game.renderer.delay)
        game.renderer.move(game.board, move_path)

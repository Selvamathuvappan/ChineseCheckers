import time
from   typing                   import TYPE_CHECKING

from   board.coin               import Coin
from   board.metrics            import DistanceMetrics

if TYPE_CHECKING:
    from game import GameManager

from   geometry.point           import Point
from   player.base              import IOInterface, Player


class ComputerPlayer(Player):

    def evaluate(self, game: "GameManager", coin: Coin, dst: Point):
        valuation_engine = DistanceMetrics(game.renderer.mutator.board)
        return (
            valuation_engine.positive_distance(coin, dst),
            valuation_engine.distance(coin.point, dst),
        )

    def get_best_move(self, game: "GameManager", coin: Coin):
        moves = game.renderer.mutator.valid_moves(coin)
        if not moves:
            return None
        return max(moves, key=lambda dst: self.evaluate(game, coin, dst))

    def compute_move(self, game: "GameManager"):
        coins = [
            coin
            for coin in game.renderer.mutator.get_all_coins()
            if game.is_players_coin(coin, self)
        ]
        coin_move_map = {
            coin: move for coin in coins if (move := self.get_best_move(game, coin))
        }
        coin_to_move = max(
            coin_move_map,
            key=lambda coin: self.evaluate(game, coin, coin_move_map[coin]),
        )
        return coin_to_move, coin_move_map[coin_to_move]

    def perform_turn(self, game: "GameManager", io: IOInterface):
        coin, dst = self.compute_move(game)
        game.renderer.highlight({coin.point})
        game.renderer.render()
        move_path = game.renderer.mutator.steps(coin, dst)
        time.sleep(game.renderer.delay)
        game.renderer.move(move_path)

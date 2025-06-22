from   abc                      import abstractmethod
import logging
import time
from   typing                   import Optional, TYPE_CHECKING

from   board                    import Coin
from   board.metrics            import DistanceMetrics
from   geometry                 import Point
from   player.base              import IOInterface, Player
from   player.minmax.state      import GameStateWrapper, MinMaxState, Move
from   state.board_state        import BoardState

if TYPE_CHECKING:
    from game import GameManager
logger = logging.getLogger(__name__)


class ComputerPlayer(Player):
    @abstractmethod
    def compute_move(self, game: "GameManager") -> tuple[Coin, Point]:
        """
        Computes the best move for the player.
        Returns a (coin, destination) tuple.
        """
        pass

    def perform_turn(self, game: "GameManager", io: IOInterface) -> None:
        """
        Performs a turn by selecting and executing the best move.
        """
        coin, dst = self.compute_move(game)
        game.renderer.highlight(game.board_state, {coin.point})
        move_path = game.steps(coin, dst)
        time.sleep(game.renderer.delay)
        game.renderer.move(game.board_state, move_path)


class GreedyPlayer(ComputerPlayer):
    """
    A computer player that selects moves greedily based on distance metrics.
    """

    @staticmethod
    def evaluate(
        board_state: BoardState, coin: Coin, dst: Point
    ) -> tuple[float, float]:
        """
        Evaluate a move for a coin to a destination using distance metrics.
        Returns a tuple for sorting preference.
        """
        valuation_engine = DistanceMetrics(board_state.board)
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
        return max(moves, key=lambda dst: self.evaluate(game.board_state, coin, dst))

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
            key=lambda coin: self.evaluate(game.board_state, coin, coin_move_map[coin]),
        )
        return coin_to_move, coin_move_map[coin_to_move]


class MinMaxPlayer(ComputerPlayer):
    """
    A player that uses the Minimax algorithm to compute the best move.
    This is a placeholder for future implementation.
    """

    def __init__(self, player_id: int, depth: int = 3, top_k: int = 5) -> None:
        super().__init__(player_id)
        self.depth = depth
        self.top_k = top_k

    @staticmethod
    def minimax_ab(
        state: MinMaxState,
        depth: int,
        top_k: int,
        total_players: int,
        maximizing_player: Player,
        alpha=float("-inf"),
        beta=float("inf"),
    ) -> tuple[float, Optional[Move]]:
        """
        Minimax algorithm with alpha-beta pruning.
        """
        if depth == 0 or state.is_terminal():
            return state.evaluate(), None

        current = state.current_player()
        legal_moves = state.get_legal_moves()[:top_k]
        logger.debug(
            f"Current player: {current}, Depth: {depth}, Legal moves: {legal_moves}"
        )
        best_move = None

        if current == maximizing_player:
            value = float("-inf")
            for move in legal_moves:
                next_state = state.apply_move(move)
                child_score, _ = MinMaxPlayer.minimax_ab(
                    next_state,
                    depth - 1,
                    top_k,
                    total_players,
                    maximizing_player,
                    alpha,
                    beta,
                )
                if best_move is None or child_score > value:
                    value = child_score
                    best_move = move
                alpha = max(alpha, value)
                if beta <= alpha:
                    break  # Beta cutoff
            return value, best_move
        else:
            # Treat others as adversarial: minimize max player's score
            value = float("inf")
            for move in legal_moves:
                next_state = state.apply_move(move)
                child_score, _ = MinMaxPlayer.minimax_ab(
                    next_state,
                    depth - 1,
                    top_k,
                    total_players,
                    maximizing_player,
                    alpha,
                    beta,
                )
                if best_move is None or child_score < value:
                    value = child_score
                    best_move = move
                beta = min(beta, value)
                if beta <= alpha:
                    break  # Alpha cutoff
            return value, best_move

    def compute_move(self, game: "GameManager") -> tuple[Coin, Point]:
        _, move = self.minimax_ab(
            GameStateWrapper(game.game_state, self),
            self.depth,
            self.top_k,
            len(game.players),
            self,
        )
        if move is None:
            raise ValueError(f"No valid moves available for Player {self.player_id}.")
        logger.debug(f"Computed move: {move}")
        return move.coin, move.dst

from   abc                      import ABC, abstractmethod
import copy
from   dataclasses              import dataclass
import functools
import logging
from   typing                   import Optional

from   board                    import Coin
from   board.metrics            import DistanceMetrics
from   geometry                 import Point
from   player.base              import Player
from   state                    import GameState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Move:
    coin: Coin
    dst: Point


class MinMaxState(ABC):
    @abstractmethod
    def current_player(self) -> int:
        """Returns the current player."""
        pass

    @abstractmethod
    def get_legal_moves(self) -> list[Move]:
        """Returns a list of all legal moves for the current player."""
        pass

    @abstractmethod
    def apply_move(self, move: Move) -> "MinMaxState":
        """Returns a new state after applying the given move."""
        pass

    @abstractmethod
    def is_terminal(self) -> bool:
        """Returns True if the state is terminal (win or no moves)."""
        pass

    @abstractmethod
    def evaluate(self) -> float:
        """Returns an evaluation score from the perspective of `player`."""
        pass


class GameStateWrapper(MinMaxState):
    """
    Wraps a GameState for use in minimax search, copying board state for isolation.
    """

    def __init__(self, game: GameState, player: Optional[Player]) -> None:
        self.game = GameState(
            board_state=copy.deepcopy(game.board_state),
            players=game.players,
            player_id_region_map=game.player_id_region_map,
            current_player_index=game.current_player_index,
        )
        self.player = player or game.current_player()

    def current_player(self) -> Player:
        """Returns the current player object."""
        return self.game.current_player()

    @functools.lru_cache(maxsize=None)
    def get_legal_moves_for_coin(
        self, coin: Coin
    ) -> list[tuple[Move, tuple[float, float]]]:
        """
        Returns a list of (Move, metrics) tuples for all legal moves for a given coin.
        """
        from player.computer import GreedyPlayer

        return [
            (Move(coin, dst), GreedyPlayer.evaluate(self.game.board_state, coin, dst))
            for dst in self.game.valid_moves(coin)
        ]

    def get_legal_moves(self) -> list[Move]:
        """
        Returns all legal moves for the current player, sorted by move score.
        """
        move_scores = [
            (move, score)
            for coin in self.game.get_all_coins()
            if self.game.is_players_coin(coin)
            for move, score in self.get_legal_moves_for_coin(coin)
        ]
        if not move_scores:
            return []
        move_scores.sort(key=lambda ms: ms[1], reverse=True)
        logger.debug(
            f"Legal moves for player {self.player.player_id}: {move_scores[:5]} (total: {len(move_scores)})"
        )
        return [move for move, _ in move_scores]

    def apply_move(self, move: Move) -> "MinMaxState":
        """
        Returns a new GameStateWrapper after applying the given move and advancing the turn.
        """
        new_game = GameStateWrapper(self.game, self.player)
        new_game.game.board_state.move_coin(move.coin.point, move.dst)
        new_game.game.next_turn()
        return new_game

    def is_terminal(self) -> bool:
        """
        Returns True if the current player has won or has no legal moves.
        """
        return self.game.has_current_player_won() or not self.get_legal_moves()

    def get_destination(self, coin: Coin) -> Point:
        """Returns the destination wedge corner point for a coin based on its region."""
        return next(
            point
            for point in self.game.board.corners
            if self.game.board.region(point)
            == self.game.board.opposite_region(coin.region)
        )

    def get_source(self, coin: Coin) -> Point:
        """Returns the source wedge corner  point for a coin based on its region."""
        return next(
            point
            for point in self.game.board.corners
            if self.game.board.region(point) == coin.region
        )

    def isolated_coin_penalty(self, coin: Coin) -> float:
        """
        Returns a penalty for isolated coins.
        If a coin has no legal moves longer than 2 steps, it is considered isolated.
        """
        coin_moves_scores = self.get_legal_moves_for_coin(coin)
        # Extract the first metric (positive step length) from each move's metrics
        max_step = (
            max(metric[0] for _, metric in coin_moves_scores)
            if coin_moves_scores
            else 0
        )
        return min(max_step - 3, 0)

    def evaluate(self) -> float:
        """
        Returns an evaluation score for the current state from the perspective of self.player.
        Penalizes coins left behind and rewards coins closer to their destination.
        """
        score = 0
        for coin in self.game.get_all_coins():
            source, destination = self.get_source(coin), self.get_destination(coin)
            distance_left: int = DistanceMetrics(self.game.board).distance(
                coin.point, destination
            )
            total_distance = DistanceMetrics(self.game.board).distance(
                source, destination
            )
            if self.game.is_players_coin(coin, self.player):
                score -= distance_left
                is_left_behind = distance_left > total_distance / 3
                if is_left_behind:
                    penalty = self.isolated_coin_penalty(coin)
                    score += penalty
                    logger.debug(
                        f"Evaluating {coin}: "
                        f"distance left {distance_left}, total distance {total_distance}, "
                        f"penalty: {penalty}"
                    )
            else:
                score += distance_left
        return score

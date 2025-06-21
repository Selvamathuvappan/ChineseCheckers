# from abc import ABC, abstractmethod
# from dataclasses import dataclass

# from board import Coin
# from geometry import Point
# from player.base import Player
# from state import GameState


# @dataclass(frozen=True)
# class Move:
#     coin: Coin
#     dst: Point

# class MinMaxState(ABC):
#     @abstractmethod
#     def current_player(self) -> int:
#         pass

#     @abstractmethod
#     def get_legal_moves(self) -> list[Move]:
#         pass

#     @abstractmethod
#     def apply_move(self, move: Move) -> 'MinMaxState':
#         pass

#     @abstractmethod
#     def is_terminal(self) -> bool:
#         pass

#     @abstractmethod
#     def evaluate(self, player: Player) -> float:
#         """Evaluation from the point of view of `player`."""
#         pass

# class GameStateWrapper:
#     def __init__(self, game: GameState):
#         self.game = game

#     def current_player(self):
#         return self.game.current_player()

#     def get_legal_moves(self):
#         return [

#             for coin in self.game.get
#         ]

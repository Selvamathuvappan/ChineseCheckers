import copy
from   typing                   import Iterable, Optional
from   venv                     import logger

from   board                    import Coin
from   board.layout             import LayoutInterface
from   geometry                 import Point


class BoardState:
    """
    Encapsulates the current state of the board including coin positions and valid move logic.
    """

    def __init__(self, board: LayoutInterface, coins: Iterable[Coin]) -> None:
        self.board = copy.deepcopy(board)
        self.point_coin_map: dict[Point, Coin] = {}
        for coin in coins:
            self.set_coin(coin)

    def get_all_points(self) -> list[Point]:
        """Returns all valid points on the board."""
        return list(self.board)

    def get_all_coins(self) -> list[Coin]:
        """Returns a list of all coins currently on the board."""
        return list(self.point_coin_map.values())

    def has_coin(self, point: Point) -> bool:
        """True if there is a coin at the given point."""
        return point in self.point_coin_map

    def get_coin(self, point: Point) -> Optional[Coin]:
        """Returns the coin at a given point, or None if empty."""
        return self.point_coin_map.get(point)

    def set_coin(self, coin: Coin) -> None:
        """Places a coin at its point on the board."""
        assert coin.point in self.board, f"Invalid coin location: {coin.point}"
        self.point_coin_map[coin.point] = coin

    def remove_coin_at(self, point: Point) -> Coin:
        """Removes and returns the coin at the given point."""
        assert point in self.point_coin_map, f"No coin at: {point}"
        return self.point_coin_map.pop(point)

    def move_coin(self, src: Point, dst: Point) -> None:
        """Moves a coin from src to dst."""
        coin = self.remove_coin_at(src)
        self.set_coin(Coin(dst, coin.region))

    def children(self, coin: Coin, cur: Point) -> list[tuple[Point, bool]]:
        """
        Computes all valid adjacent or jump moves from the current point for a given coin.

        Returns:
            List of (next_point, is_jump) pairs.
        """
        children: list[tuple[Point, bool]] = []
        for delta in self.board.directions:
            step = cur + delta
            if not self.get_coin(step):
                if self.board.can_enter(coin, step):
                    children.append((step, False))
            else:
                jump = step + delta
                if not self.get_coin(jump) and self.board.can_enter(coin, jump, True):
                    children.append((jump, True))
        return children

    def valid_moves(self, coin: Coin) -> set[Point]:
        """
        Computes all valid moves for the given coin using DFS with jump chaining.

        Returns:
            Set of all reachable positions.
        """
        parent = self.valid_moves_helper(coin)
        return {point for point in parent if self.board.can_enter(coin, point)}

    def valid_moves_helper(self, coin: Coin) -> dict[Point, Point]:
        """
        Computes all reachable positions for the given coin using DFS with jump chaining.

        Returns:
            Dict of all reachable positions mapped to their previous positions.
        """
        dfs_stack = [coin.point]
        visited: set[Point] = set()
        finished: set[Point] = set()
        parent: dict[Point, Point] = {}
        while dfs_stack:
            cur = dfs_stack[-1]
            if cur in visited:
                dfs_stack.pop()
                for nxt, is_jump in self.children(coin, cur):
                    if is_jump and nxt in finished:
                        parent[nxt] = cur
                finished.add(cur)
            else:
                visited.add(cur)
                for nxt, is_jump in self.children(coin, cur):
                    if is_jump and nxt not in finished:
                        dfs_stack.append(nxt)

        # Add immediate non-jump steps
        for nxt, is_jump in self.children(coin, coin.point):
            if not is_jump:
                parent[nxt] = cur
        logger.debug(f"Valid moves for {coin}: {parent}")
        return parent

    def steps(self, coin: Coin, point: Optional[Point]) -> list[Point]:
        """
        Reconstructs the path from the original coin location to the given point.

        Returns:
            Ordered path of moves.
        """
        parent = self.valid_moves_helper(coin)
        path: list[Point] = []
        while point:
            path.append(point)
            point = parent.get(point)
        return path[::-1]

    def coin_at_destination(self, coin: Coin) -> bool:
        """Checks if coin has reached its destination region/color"""
        return self.board.region(coin.point) == self.board.opposite_region(coin.region)

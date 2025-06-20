import copy
from   typing                   import Iterable

from   board                    import Coin
from   board.layout             import LayoutInterface
from   geometry                 import Point


class BoardState:
    """
    Encapsulates the current state of the board including coin positions and valid move logic.
    """

    def __init__(self, board: LayoutInterface, coins: Iterable[Coin]):
        self.board = copy.deepcopy(board)
        self.point_coin_map: dict[Point, Coin] = {}
        for coin in coins:
            self.set_coin(coin)
        self._dfs_parent = {}

    def get_all_points(self):
        """Returns all valid points on the board."""
        return list(self.board)

    def get_all_coins(self):
        """Returns a list of all coins currently on the board."""
        return [coin for coin in self.point_coin_map.values()]

    def has_coin(self, point: Point) -> bool:
        """Checks if there is a coin at the given point."""
        return point in self.point_coin_map

    def get_coin(self, point: Point) -> Coin | None:
        """Returns the coin at a given point, if any."""
        return self.point_coin_map.get(point)

    def set_coin(self, coin: Coin):
        """Places a coin at its point on the board."""
        assert coin.point in self.board, f"Invalid coin location: {coin.point}"
        self.point_coin_map[coin.point] = coin

    def remove_coin_at(self, point: Point) -> Coin:
        """Removes and returns the coin at the given point."""
        assert point in self.point_coin_map, f"No coin at: {point}"
        return self.point_coin_map.pop(point)

    def move_coin(self, src: Point, dst: Point):
        """Moves a coin from src to dst and updates the internal state."""
        coin = self.remove_coin_at(src)
        self.set_coin(Coin(dst, coin.region))
        return self.board

    def children(self, coin: Coin, cur: Point):
        """
        Computes all valid adjacent or jump moves from the current point for a given coin.

        Returns:
            list[tuple[Point, bool]]: A list of (next_point, is_jump) pairs.
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

    def valid_moves(self, coin: Coin):
        """
        Computes all reachable positions for the given coin using DFS with jump chaining.

        Returns:
            set[Point]: All reachable positions.
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
                finished.add(nxt)
                parent[nxt] = cur
        self._dfs_parent = parent
        finished.remove(coin.point)
        return {point for point in finished if self.board.can_enter(coin, point)}

    def steps(self, coin: Coin, point: Point | None):
        """
        Reconstructs the path from the original coin location to the given point.

        Returns:
            list[Point]: Ordered path of moves.
        """
        self.valid_moves(coin)
        path = []
        while point:
            path.append(point)
            point = self._dfs_parent.get(point)
        return path[::-1]

    def coin_at_destination(self, coin: Coin):
        """Checks if coin has reached its destination region/color"""
        return self.board.region(coin.point) == self.board.opposite_region(coin.region)

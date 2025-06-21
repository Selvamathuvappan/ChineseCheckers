from   abc                      import ABC, abstractmethod
import logging
from   typing                   import Iterable, Iterator, Optional

from   board                    import Coin, constants
from   geometry                 import Line, Point
from   geometry.utils           import (get_line_intersection,
                                        get_trapping_lines, point_enclosed_by)
from   utils                    import sign

logger = logging.getLogger(__name__)


class LayoutInterface(ABC):
    """
    Abstract base class for board layouts. Concrete board layouts should implement
    direction rules, validity of coins and entry rules.
    """

    def __init__(self, side_count: int) -> None:
        self.n = side_count

    @property
    @abstractmethod
    def directions(self) -> Iterable[Point]:
        """
        Returns all possible movement directions from a given point.
        """
        pass

    @abstractmethod
    def positive_direction(self, region: int) -> Point:
        """
        Returns positive movement directions for a given region.
        """
        pass

    @abstractmethod
    def __contains__(self, point: Point) -> bool:
        """
        Returns True if the point is on the board.
        """
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[Point]:
        """
        Iterates through the points on the board.
        """
        pass

    @abstractmethod
    def can_enter(self, coin: Coin, point: Point, is_jump: bool = False) -> bool:
        """
        Returns True if the given coin can enter the specified point.
        """
        pass

    @abstractmethod
    def is_valid_coin(self, coin: Coin) -> bool:
        """
        Returns True if the coin is initially allowed at its position.
        """
        pass

    @abstractmethod
    def region(self, point: Point) -> Optional[int]:
        """
        Get the region index [0–n] a point lies in.

        Returns:
            int | None: Region index or None if point is invalid.
        """
        pass

    def opposite_region(self, region: int) -> Optional[int]:
        """
        Get the destinsation region for coins at input region.

        Returns:
            int | None: Region index or None if point is invalid.
        """
        if region == 0:
            return None
        region -= 1
        return (region + self.n // 2) % self.n + 1


class Layout(LayoutInterface):
    """
    Concrete implementation of LayoutInterface for a polygonal Chinese Checkers board.
    Handles region detection, movement validation, and geometric bounds.
    """

    def __init__(self, side_count: int) -> None:
        """Initialize the board layout given the number of polygon sides/regions (typically 4, 6, or 8)."""
        super().__init__(side_count)
        central_polygon = constants.REGION_POLYGON_MAP[side_count]
        self.central_polygon = central_polygon

    @property
    def directions(self) -> Iterable[Point]:
        return constants.DIRECTIONS

    def positive_direction(self, region: int) -> Point:
        """Returns the movement direction towards opposite/destination region for a given region."""
        assert region, "Positive direction is only defined for non-central regions."
        a, b, c = self.central_polygon[region - 1]
        return Point(-a * sign(c), -b * sign(c))

    @property
    def outer_polygon(self) -> list[list[Line]]:
        """Constructs outer bounding line pairs that form each region's wedge."""
        bounding_line_pairs: list[list[Line]] = []
        prev, cur, nxt = -1, 0, 1
        while cur < self.n:

            p1 = get_line_intersection(
                self.central_polygon[cur], self.central_polygon[prev]
            )
            p2 = get_line_intersection(
                self.central_polygon[cur], self.central_polygon[nxt]
            )

            if p1 and p2:
                assert tuple(map(int, p1)) == p1
                assert tuple(map(int, p2)) == p2
                p1, p2 = map(int, p1), map(int, p2)
                p1, p2 = Point(*p1), Point(*p2)
                l1, l2 = get_trapping_lines(p1, p2)
                bounding_line_pairs.append([l1, l2])
            prev = (prev + 1) % self.n
            cur = cur + 1
            nxt = (nxt + 1) % self.n
        return bounding_line_pairs

    @property
    def corners(self) -> list[Point]:
        """
        Get outer polygon/wedge corners by intersecting outer lines.
        """
        corners = [
            point
            for l1, l2 in self.outer_polygon
            if (point := get_line_intersection(l1, l2))
        ]
        assert all(tuple(map(int, point)) == tuple(point) for point in corners)
        return [Point(*map(int, corner)) for corner in corners]

    @property
    def x_bounds(self) -> tuple[int, int]:
        x_corners, _ = zip(*self.corners)
        return min(x_corners), max(x_corners)

    @property
    def y_bounds(self) -> tuple[int, int]:
        _, y_corners = zip(*self.corners)
        return min(y_corners), max(y_corners)

    def __contains__(self, point: Point) -> bool:
        """Determine if a point lies inside the layout."""
        if (point.x + point.y) & 1:
            return False
        if not (
            min(self.x_bounds) <= point.x <= max(self.x_bounds)
            and min(self.y_bounds) <= point.y <= max(self.y_bounds)
        ):
            return False

        if all(line.is_origin_side(point) for line in self.central_polygon):
            return True

        if any(
            point_enclosed_by(point, line, line_pair)
            for line, line_pair in zip(self.central_polygon, self.outer_polygon)
        ):
            return True

        return False

    def __iter__(self) -> Iterator[Point]:
        """Iterate through all points within the board layout."""
        for x in range(min(self.x_bounds), max(self.x_bounds) + 1):
            for y in range(min(self.y_bounds), max(self.y_bounds) + 1):
                if Point(x, y) in self:
                    yield Point(x, y)

    def region(self, point: Point) -> Optional[int]:
        """Get the region index [0–n] a point lies in."""
        if not point in self:
            return None
        for idx, (line, line_pair) in enumerate(
            zip(self.central_polygon, self.outer_polygon), start=1
        ):
            if not line.is_origin_side(point) and point_enclosed_by(
                point, line, line_pair
            ):
                return idx
        return 0

    def can_enter(
        self, coin: Coin, point: Point, relax_region_restriction: bool = False
    ):
        """
        Determine if a coin can legally move to the given point.
        Args:
            coin (Coin): The coin in question.
            point (Point): Target location.
            relax_region_restriction (bool): Allows any region entry if True. Set to true in jump moves.

        Returns:
            bool: Whether movement is valid.
        """
        coin_region = coin.region
        point_region = self.region(point)
        if coin_region is None or point_region is None:
            return False
        if not all(
            self.is_valid_region(region) for region in [coin_region, point_region]
        ):
            return False
        if point_region == 0:
            return True
        return relax_region_restriction or (
            point_region in [coin_region, self.opposite_region(coin_region)]
        )

    def is_valid_region(self, region: int) -> bool:
        return isinstance(region, int) and 0 <= region <= self.n

    def is_valid_coin(self, coin: Coin) -> bool:
        return (
            self.is_valid_region(coin.region)
            and coin.region != 0
            and coin.point in self
            and self.can_enter(coin, coin.point)
        )

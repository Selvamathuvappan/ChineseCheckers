from   typing                   import Tuple

from   geometry.point           import Point
from   utils                    import sign


class Line:
    """
    Represents a 2D line in the form ax + by = c.

    Provides methods for construction via points or direction, evaluation, and side-checking.
    """

    def __init__(self, a: int, b: int, c: int):
        assert a or b
        if a < 0 or (a == 0 and b < 0):
            a, b, c = -a, -b, -c
        self.a, self.b, self.c = a, b, c

    def __iter__(self):
        return iter((self.a, self.b, self.c))

    @classmethod
    def from_points(cls, p1: Point, p2: Point) -> "Line":
        """
        Constructs a line through two points.
        """
        dx, dy = p2 - p1
        a, b = -dy, dx
        c = a * p1.x + b * p1.y
        return cls(a, b, c)

    @classmethod
    def through(cls, point: Point, direction: Tuple[int, int]) -> "Line":
        """
        Constructs a line with the given normal direction that passes through a point.
        """
        a, b = direction
        c = a * point.x + b * point.y
        return cls(a, b, c)

    def evaluate(self, point: Point) -> int:
        """
        Evaluates the line equation for a point: ax + by - c
        """
        return self.a * point.x + self.b * point.y - self.c

    def side(self, point: Point) -> int:
        """
        Returns the sign of ax + by - c.
        +1 if point lies on positive side
        -1 if on negative side
        0 if on the line
        """
        return sign(self.evaluate(point))

    def is_origin_side(self, point: Point):
        """
        Returns True if the point lies on the same side of the line as the origin.
        """
        if self.side(point) == 0:
            return True
        return self.side(point) != sign(self.c)

    def __str__(self):
        return f"{self.a}x + {self.b}y = {self.c}"

    def __repr__(self):
        return str(self)

from   typing                   import Iterator


class Point:
    """
    Represents an immutable 2D point with integer coordinates.

    Supports:
    - Iteration
    - Addition and subtraction with other Point objects
    - Equality checks and hashing
    - String and representation formatting
    """

    def __init__(self, x: int, y: int) -> None:
        self._x, self._y = x, y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def __iter__(self) -> Iterator[int]:
        return iter((self.x, self.y))

    def __add__(self, other) -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other) -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def __eq__(self, other) -> bool:
        return isinstance(other, Point) and tuple(self) == tuple(other)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __str__(self) -> str:
        return f"Point(x={self.x}, y={self.y})"

    def __repr__(self) -> str:
        return str(self)

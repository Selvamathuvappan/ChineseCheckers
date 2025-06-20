class Point:
    """
    Represents an immutable 2D point with integer coordinates.

    Supports:
    - Iteration
    - Addition and subtraction with other Point objects
    - Equality checks and hashing
    - String and representation formatting
    """

    def __init__(self, x: int, y: int):
        self._x, self._y = x, y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __iter__(self):
        return iter((self.x, self.y))

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return isinstance(other, Point) and tuple(self) == tuple(other)

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"Point(x={self.x}, y={self.y})"

    def __repr__(self):
        return str(self)

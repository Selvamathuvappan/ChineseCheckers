from   typing                   import Iterable, List

from   geometry.line            import Line
from   geometry.point           import Point


def get_trapping_lines(p1: Point, p2: Point) -> List[Line]:
    """
    Given two points aligned along one of the base directions of the board,
    returns a pair of lines that, together with the base line through p1 and p2,
    form a wedge that doesn't trap the origin.

    These lines are used to determine the outer boundaries of a region on the board.

    Raises:
        ValueError: If no such configuration exists.
    """
    dx, dy = p2 - p1

    # Normalize direction to match one of 4 kinds
    if dx == 0:
        dirs = [(1, 1), (1, -1)]  # Vertical → Diagonals
    elif dy == 0:
        dirs = [(1, 1), (-1, 1)]  # Horizontal → Diagonals
    elif dx == -dy:
        dirs = [(0, 1), (1, -1)]  # Diagonal \ → H + /
    elif dx == dy:
        dirs = [(0, 1), (1, 1)]  # Diagonal / → H + \
    else:
        raise ValueError("Unsupported base direction")

    origin = Point(0, 0)

    # Try both assignments: (p1, dir1), (p2, dir2) and vice versa
    line = Line.from_points(p1, p2)
    for d1, d2 in [dirs, dirs[::-1]]:
        l1 = Line.through(p1, d1)
        l2 = Line.through(p2, d2)
        intersection = get_line_intersection(l1, l2)
        assert intersection and all(int(coord) == coord for coord in intersection)
        intersection = Point(*[int(coord) for coord in intersection])
        if line.side(origin) != line.side(intersection):
            return [l1, l2]

    raise ValueError("No trapping line configuration intersects opposite to origin")


def get_line_intersection(line1: Line, line2: Line):
    """
    Returns intersection point (x, y) of two lines in general form:
    a1*x + b1*y = c1
    a2*x + b2*y = c2
    Returns None if lines are parallel or coincident.
    """
    a1, b1, c1 = line1
    a2, b2, c2 = line2
    D = a1 * b2 - a2 * b1
    if D == 0:
        return None  # Lines are parallel or identical
    x = (c1 * b2 - c2 * b1) / D
    y = (a1 * c2 - a2 * c1) / D
    return (x, y)


def point_enclosed_by(point: Point, line: Line, bounding_lines: Iterable[Line]):
    """
    Returns True if `point` is strictly inside the region bounded by `bounding_lines`
    and on the opposite side of `line` from the origin.
    """
    return not line.is_origin_side(point) and all(
        outer_line.is_origin_side(point) for outer_line in bounding_lines
    )

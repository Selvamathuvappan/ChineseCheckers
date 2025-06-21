import itertools

from   geometry                 import Line, Point

SQUARE = [
    Line(0, 1, 4),
    Line(1, 0, 4),
    Line(0, 1, -4),
    Line(1, 0, -4),
]
HEXAGON = [
    Line(0, 1, 4),
    Line(1, 1, 8),
    Line(1, -1, 8),
    Line(0, 1, -4),
    Line(1, 1, -8),
    Line(1, -1, -8),
]
OCTAGON = [
    Line(0, 1, 8),
    Line(1, 1, 12),
    Line(1, 0, 8),
    Line(1, -1, 12),
    Line(0, 1, -8),
    Line(1, 1, -12),
    Line(1, 0, -8),
    Line(1, -1, -12),
]

REGION_POLYGON_MAP = {len(polygon): polygon for polygon in [SQUARE, HEXAGON, OCTAGON]}
X_STEP = 2
Y_STEP = 1
# list of direction vectors used for movement or neighborhood calculations in the board layout.
DIRECTIONS = [
    Point(x, y)
    for x, y in (
        list(itertools.product([-X_STEP // 2, X_STEP // 2], [-Y_STEP, Y_STEP]))
        + [(-X_STEP, 0), (X_STEP, 0)]
    )
]

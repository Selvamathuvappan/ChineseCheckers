from   geometry.line            import Line
from   geometry.point           import Point
from   geometry.utils           import (get_line_intersection,
                                        get_trapping_lines, point_enclosed_by)


def test_get_line_intersection():
    l1 = Line(1, -1, 0)  # x - y = 0
    l2 = Line(1, 1, 4)  # x + y = 4
    result = get_line_intersection(l1, l2)
    assert result == (2.0, 2.0)


def test_parallel_lines():
    l1 = Line(1, -1, 0)
    l2 = Line(2, -2, 0)
    result = get_line_intersection(l1, l2)
    assert result is None


def test_get_trapping_lines_vertical():
    p1 = Point(2, 0)
    p2 = Point(2, 4)
    lines = get_trapping_lines(p1, p2)
    assert len(lines) == 2
    assert all(isinstance(l, Line) for l in lines)
    assert ", ".join(map(str, lines)) == "1x + -1y = 2, 1x + 1y = 6"


def test_get_trapping_lines_diagonal():
    p1 = Point(1, 1)
    p2 = Point(4, 4)
    lines = get_trapping_lines(p1, p2)
    assert len(lines) == 2
    assert all(isinstance(l, Line) for l in lines)
    assert ", ".join(map(str, lines)) == "0x + 1y = 1, 1x + 1y = 8"


def test_point_enclosed_by():
    central = Line(1, 0, 2)  # Vertical line x = 2
    l1 = Line(1, 1, 4)  # x + y = 4
    l2 = Line(1, -1, 4)  # x - y = 4
    point = Point(3, 0)
    assert point_enclosed_by(point, central, [l1, l2]) is True


def test_point_not_enclosed():
    central = Line(1, 0, 2)
    l1 = Line(1, 1, 4)
    l2 = Line(1, -1, 4)
    point = Point(1, 0)
    assert point_enclosed_by(point, central, [l1, l2]) is False
    point = Point(5, 5)
    assert point_enclosed_by(point, central, [l1, l2]) is False

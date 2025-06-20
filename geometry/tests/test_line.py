from   geometry.line            import Line
from   geometry.point           import Point


def test_from_points_basic():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    line = Line.from_points(p1, p2)
    assert line.evaluate(Point(1, 1)) == 0
    assert line.side(Point(2, 1)) != 0


def test_through_direction():
    p = Point(2, 3)
    direction = (1, -1)
    line = Line.through(p, direction)
    assert line.evaluate(p) == 0


def test_line_evaluation():
    line = Line(1, -1, 0)
    assert line.evaluate(Point(2, 2)) == 0
    assert line.evaluate(Point(3, 1)) == 2
    assert line.evaluate(Point(1, 3)) == -2


def test_side():
    line = Line(1, 1, 5)
    assert line.side(Point(2, 2)) == -1
    assert line.side(Point(3, 3)) == 1
    assert line.side(Point(0, 5)) == 0


def test_is_origin_side():
    line = Line(1, 1, 3)
    assert line.is_origin_side(Point(0, 0)) == True
    assert line.is_origin_side(Point(5, 5)) == False
    assert line.is_origin_side(Point(1, 2)) == True  # on line


def test_normalization_enforced():
    assert list(Line(-1, 2, 3)) == [1, -2, -3]
    assert list(Line(0, -1, 5)) == [0, 1, -5]


def test_str_repr():
    line = Line(1, 2, 3)
    assert str(line) == "1x + 2y = 3"
    assert repr(line) == "1x + 2y = 3"

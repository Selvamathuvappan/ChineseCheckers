import pytest

from   geometry.point           import Point


def test_point_creation():
    p = Point(3, 4)
    assert p.x == 3
    assert p.y == 4


def test_point_addition():
    p1 = Point(1, 2)
    p2 = Point(3, 4)
    assert p1 + p2 == Point(4, 6)


def test_point_subtraction():
    p1 = Point(5, 7)
    p2 = Point(2, 3)
    assert p1 - p2 == Point(3, 4)


def test_point_equality():
    assert Point(1, 1) == Point(1, 1)
    assert Point(1, 1) != Point(2, 2)


def test_point_hash():
    p1 = Point(3, 4)
    p2 = Point(3, 4)
    s = set([p1, p2])
    assert len(s) == 1


def test_point_str():
    p = Point(3, 4)
    assert str(p) == "Point(x=3, y=4)"


def test_mutate_point():
    with pytest.raises(AttributeError):
        p = Point(3, 4)
        p.x = 10  # type: ignore

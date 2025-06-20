import pytest

from   board.coin               import Coin
from   board.layout             import Layout
from   geometry.point           import Point


@pytest.mark.parametrize("side_count", [4, 6, 8])
def test_layout_contains_all_corners(side_count):
    layout = Layout(side_count)
    for corner in layout.corners:
        assert corner in layout


def test_layout_contains_origin():
    layout = Layout(6)
    assert Point(0, 0) in layout


def test_layout_excludes_odd_sum_points():
    layout = Layout(6)
    assert Point(1, 0) not in layout
    assert Point(0, 1) not in layout


def test_iteration_over_layout():
    layout = Layout(6)
    all_points = list(layout)
    for p in all_points:
        assert p in layout


def test_region_values():
    layout = Layout(6)
    assert layout.region(Point(0, 0)) == 0
    assert layout.region(Point(100, 100)) is None


def test_opposite_region():
    layout = Layout(6)
    assert layout.opposite_region(1) == 4
    assert layout.opposite_region(0) is None


def test_can_enter():
    layout = Layout(6)
    coin = Coin(point=Point(2, 6), region=1)
    assert layout.can_enter(coin, Point(0, 0)) is True  # center
    # Enter opposite region
    target = [p for p in layout if layout.region(p) == layout.opposite_region(1)]
    assert any(layout.can_enter(coin, p) for p in target)


def test_invalid_coins():
    layout = Layout(6)
    assert not layout.is_valid_coin(Coin(point=Point(6, 4), region=1))
    assert not layout.is_valid_coin(Coin(point=Point(200, 200), region=2))
    assert not layout.is_valid_coin(Coin(point=Point(0, 0), region=99))


def test_valid_coin():
    layout = Layout(6)
    point = next(p for p in layout if layout.region(p) == 1)
    assert layout.is_valid_coin(Coin(point=point, region=1))

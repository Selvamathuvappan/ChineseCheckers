import pytest

from   board.coin               import Coin
from   board.layout             import Layout
from   geometry                 import Point


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


def test_can_enter_relaxed():
    layout = Layout(6)
    coin = Coin(point=Point(2, 6), region=1)
    # Should allow entry anywhere with is_jump=True
    for p in layout:
        assert layout.can_enter(coin, p, True)


def test_invalid_coins():
    layout = Layout(6)
    assert not layout.is_valid_coin(Coin(point=Point(6, 4), region=1))
    assert not layout.is_valid_coin(Coin(point=Point(200, 200), region=2))
    assert not layout.is_valid_coin(Coin(point=Point(0, 0), region=99))
    with pytest.raises(AssertionError):
        Coin(Point(0, 0), region=0)


def test_valid_coin():
    layout = Layout(6)
    point = next(p for p in layout if layout.region(p) == 1)
    assert layout.is_valid_coin(Coin(point=point, region=1))


def test_positive_direction_type_and_value():
    layout = Layout(6)
    direction = layout.positive_direction(1)
    assert isinstance(direction, Point)
    # Should not be zero vector
    assert direction.x != 0 or direction.y != 0


def test_x_bounds_and_y_bounds():
    layout = Layout(6)
    x_min, x_max = layout.x_bounds
    y_min, y_max = layout.y_bounds
    assert x_min < x_max
    assert y_min < y_max


def test_outer_polygon_and_corners():
    layout = Layout(6)
    assert len(layout.outer_polygon) == 6
    assert len(layout.corners) == 6


def test_contains_out_of_bounds():
    layout = Layout(6)
    assert Point(1000, 1000) not in layout
    assert Point(-1000, -1000) not in layout


@pytest.mark.parametrize("region", [0, 1, 6, 99, -1])
def test_is_valid_region(region):
    layout = Layout(6)
    if region in range(0, 7):
        assert layout.is_valid_region(region)
    else:
        assert not layout.is_valid_region(region)


def test_all_regions_unique_and_covered():
    layout = Layout(6)
    regions = set()
    for p in layout:
        r = layout.region(p)
        if r is not None:
            regions.add(r)
    assert regions == set(range(0, 7))

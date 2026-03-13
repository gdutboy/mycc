import pytest

from core.region import InvalidRegionError, normalize_region


def test_invalid_region_when_width_or_height_not_positive():
    with pytest.raises(InvalidRegionError):
        normalize_region([0, 0, 0, 10], [0, 0, 1920, 1080])


def test_region_is_clipped_to_screen_bounds():
    assert normalize_region([-10, -10, 30, 30], [0, 0, 100, 100]) == [0, 0, 20, 20]

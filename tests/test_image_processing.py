from dataclasses import dataclass
from unittest.mock import patch, MagicMock

import numpy as np
import pytest

from src.util.image_processing import (
    get_palette,
    get_user_palette,
    closest_color,
    get_average_color,
    create_color_scheme,
    get_contrast_color
)

@dataclass
class GetPalette:
    result: dict[int: tuple[int, int, int]]

GetPaletteCases = [
    GetPalette(
        result={1: (255, 255, 255)}
    ),
    GetPalette(
        result={1: (0, 0, 0), 2: (255, 255, 255)}
    ),
    GetPalette(
        result={3: (128, 128, 128), 4: (64, 64, 64), 5: (192, 192, 192)}
    ),
    GetPalette(
        result={10: (0, 0, 0)}
    )
]

@dataclass
class ClosestColor:
    color: tuple[int, int, int]
    palette1: dict[int, tuple[int, int, int]]
    palette2: dict[int, tuple[int, int, int]]
    result: int

ClosestColorCases = [
    ClosestColor(
        color=(200, 200, 200),
        palette1={1: (100, 100, 100)},
        palette2={2: (255, 255, 255)},
        result=2
    ),
    ClosestColor(
        color=(90, 90, 90),
        palette1={1: (80, 80, 80)},
        palette2={2: (100, 100, 100)},
        result=2
    ),
    ClosestColor(
        color=(200, 50, 50),
        palette1={1: (200, 50, 50)},
        palette2={2: (150, 50, 50)},
        result=1
    ),
    ClosestColor(
        color=(255, 0, 0),
        palette1={1: (0, 255, 0)},
        palette2={2: (0, 0, 255)},
        result=2
    )
]

@pytest.mark.parametrize('case', GetPaletteCases)
@patch("src.util.image_processing.GammaHandler")
def test_get_palette(mock_gamma_handler, case: GetPalette):
    mock_handler_instance = MagicMock()
    mock_handler_instance.select_palette.return_value = case.result
    mock_gamma_handler.return_value = mock_handler_instance

    result = get_palette()
    assert result == case.result
    mock_handler_instance.teardown.assert_called_once()


@patch("src.util.image_processing.GammaHandler")
@patch("src.util.image_processing.UserAvailableHandler")
def test_get_user_palette(mock_user_handler, mock_gamma_handler):
    mock_user_instance = MagicMock()
    mock_user_instance.select_colors.return_value = [1]
    mock_user_handler.return_value = mock_user_instance

    mock_gamma_instance = MagicMock()
    mock_gamma_instance.get_rgb.return_value = (255, 255, 255)
    mock_gamma_handler.return_value = mock_gamma_instance

    result = get_user_palette()
    assert result == {1: (255, 255, 255)}
    mock_user_instance.teardown.assert_called_once()
    mock_gamma_instance.teardown.assert_called_once()


@pytest.mark.parametrize("case", ClosestColorCases)
def test_closest_color(case: ClosestColor):
    alpha = 100
    result = closest_color(case.color, case.palette1, case.palette2, alpha)
    assert result == case.result


def test_get_average_color():
    block = np.array([[[100, 100, 100], [150, 150, 150]], [[200, 200, 200], [250, 250, 250]]])
    result = get_average_color(block)
    assert result == (175, 175, 175)


@patch("src.util.image_processing.get_average_color", return_value=(200, 200, 200))
@patch("src.util.image_processing.closest_color", return_value="1")
def test_create_color_scheme(mock_closest_color, mock_get_average_color):
    mock_image = MagicMock()
    mock_image.shape = (10, 10, 3)
    mock_image_array = np.zeros((10, 10, 3), dtype=np.uint8)
    mock_image.__array__ = MagicMock(return_value=mock_image_array)
    palette = {"1": (255, 255, 255)}

    user_palette = {}

    scheme, color_counts = create_color_scheme(mock_image, 5, palette, user_palette)

    assert scheme == [["1", "1"], ["1", "1"]]
    assert color_counts == {"1": 4}

@pytest.mark.parametrize(
    "r, g, b, expected",
    [
        (255, 255, 255, [0, 0, 0]),
        (0, 0, 0, [1, 1, 1]),
        (123, 123, 123, [1, 1, 1]),
        (200, 200, 200, [0, 0, 0]),
        (50, 150, 250, [1, 1, 1]),
        (0, 0, 0, [1, 1, 1]),
        (255, 255, 255, [0, 0, 0]),
        (128, 128, 128, [1, 1, 1]),
        (40, 100, 200, [1, 1, 1]),
        (180, 60, 30, [1, 1, 1]),
        (250, 250, 250, [0, 0, 0])
    ],
    ids=[f"case{i}" for i in range(11)]
)
def test_get_contrast_color(r, g, b, expected):
    result = get_contrast_color(r, g, b)
    assert result == expected
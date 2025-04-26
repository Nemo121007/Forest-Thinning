"""Module for general functions used in the application.

This module contains functions for validating user input and converting data types.
It includes functions for validating names, floats, and integers.
It also includes functions for converting strings to integers and floats.
"""

import re
from .Settings import Settings


def validate_name(test_line: str) -> bool:
    """Validate if a string contains only Russian/English letters or digits.

    Checks if the input string matches a regular expression allowing only:
    - Russian letters (А-Я, а-я)
    - English letters (A-Z, a-z)
    - Digits (0-9)

    Args:
        test_line (str): The string to validate.

    Returns:
        bool: True if the string contains only allowed characters, False if empty or invalid.

    Raises:
        TypeError: If test_line is not a string.
    """
    if not test_line or test_line == "":
        return False

    pattern = r"^[а-яА-Яa-zA-Z0-9]+$"
    return bool(re.match(pattern, test_line))


def validate_float(test_line: str) -> float | None:
    """Validate and convert a string to a float.

    Replaces commas with dots and attempts to convert the string to a float.

    Args:
        test_line (str): The string to validate and convert.

    Returns:
        float | None: The converted float value if successful, None if empty or invalid.

    Raises:
        TypeError: If test_line is not a string.
    """
    if not test_line or test_line == "":
        return None
    test_line = test_line.replace(",", ".")
    try:
        return float(test_line)
    except ValueError:
        return None


def fix_monotony(array: list[float]) -> list[float]:
    """Ensure an array is monotonically non-decreasing.

    Modifies the input array in-place by setting each element to be at least as large as
    the previous element, ensuring monotonicity.

    Args:
        array (list[float]): The input array of floating-point numbers.

    Returns:
        list[float]: The modified array, now monotonically non-decreasing.

    Raises:
        TypeError: If array is not a list or contains non-numeric elements.
    """
    for i in range(1, len(array)):
        if array[i] < array[i - 1]:
            array[i] = array[i - 1]
    return array


def cast_coordinates_point(x: float, y: float) -> tuple[float, float]:
    """Round coordinates to the nearest grid steps for plotting.

    Rounds the x and y coordinates to the nearest multiples of `Settings.STEP_PLOTTING_GRAPH`
    and `Settings.STEP_VALUE_GRAPH`, respectively, to align with the plotting grid.

    Args:
        x (float): The x-coordinate to round.
        y (float): The y-coordinate to round.

    Returns:
        tuple[float, float]: A tuple of (rounded_x, rounded_y) coordinates.

    Raises:
        TypeError: If x or y is not a number.
    """
    x = round(x / Settings.STEP_PLOTTING_GRAPH) * Settings.STEP_PLOTTING_GRAPH
    y = round(y / Settings.STEP_VALUE_GRAPH) * Settings.STEP_VALUE_GRAPH
    return x, y

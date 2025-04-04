"""Module for general functions used in the application.

This module contains functions for validating user input and converting data types.
It includes functions for validating names, floats, and integers.
It also includes functions for converting strings to integers and floats.
"""

import re


def validate_name(test_line: str) -> bool:
    """Validates if string contains only Russian/English letters or digits.

    Uses regular expression to check if the string contains only allowed characters:
    - Russian letters (А-Я, а-я)
    - English letters (A-Z, a-z)
    - Digits (0-9)

    Args:
        test_line (str): String to validate

    Returns:
        bool: True if string contains only allowed characters, False otherwise
    """
    if not test_line or test_line == "":
        return False

    pattern = r"^[а-яА-Яa-zA-Z0-9]+$"
    return bool(re.match(pattern, test_line))


def validate_float(test_line: str) -> float | None:
    """Validates if string can be converted to a float.

    Replaces commas with dots and checks if the string can be converted to a float.

    Args:
        test_line (str): String to validate
    Returns:
        float | None: Float value if conversion is successful, None otherwise
    """
    if not test_line or test_line == "":
        return None
    test_line = test_line.replace(",", ".")
    try:
        return float(test_line)
    except ValueError:
        return None

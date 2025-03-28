"""Module of Type_line enum."""

from enum import Enum
import re


class Type_line(Enum):
    """Enum of line types.

    Attributes:
        MIN_LEVEL_LOGGING (str): min level logging
        MAX_LEVEL_LOGGING (str): max level logging
        ECONOMIC_MAX_LINE (str): economic max line
        ECONOMIC_MIN_LINE (str): economic min line
        STANDARD_GROWTH_LINE (str): standard growth line
        GROWTH_LINE (str): growth line
        RECOVERY_LINE (str): recovery line
    """

    MIN_LEVEL_LOGGING = "min level logging"
    MAX_LEVEL_LOGGING = "max level logging"
    ECONOMIC_MAX_LINE = "economic max line"
    ECONOMIC_MIN_LINE = "economic min line"
    STANDARD_GROWTH_LINE = "standard growth line"
    GROWTH_LINE = "growth line"
    RECOVERY_LINE = "recovery line"

    @staticmethod
    def give_enum_from_value(value: str) -> "Type_line":
        """Give enum from value.

        Args:
            value (str): Value of enum.

        Returns:
            Type_line: Enum of value.
        """
        if re.match(r"growth line \d+", value):
            return Type_line.GROWTH_LINE
        elif re.match(r"recovery line \d+", value):
            return Type_line.RECOVERY_LINE
        else:
            try:
                return Type_line(value)
            except ValueError as e:
                raise ValueError(f"Unidentified line type\n Logs:\n {e}")

"""This module defines an enumeration for different types of actions.

It is used to categorize actions that can be performed in the application.
"""

from enum import Enum


class TypeAction(Enum):
    """Enumeration for different types of actions."""

    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"

    def __str__(self) -> str:
        """Returns the string value of Type_settings enumeration member.

        Returns:
            str: The string representation of the enumeration value
        """
        return self.value

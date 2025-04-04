"""Enumeration of forest settings types.

This enum defines different types of forest settings that can be used in the application.

    AREA (str): Area of the forest setting type
    BREED (str): Breed or species of trees in the forest
    CONDITION (str): Condition/state of the forest

Methods:
    __str__(): Returns string representation of the setting type
"""

from enum import Enum


class TypeSettings(Enum):
    """Enum type settings.

    Attributes:
        GRAPH_SETTINGS: settings graphic
        COLOR_SETTINGS: settings color
        SYSTEM_SETTINGS: settings system
    """

    AREA = "Регион"
    BREED = "Порода"
    CONDITION = "Условия"
    GRAPHIC = "График"

    def __str__(self) -> str:
        """Returns the string value of Type_settings enumeration member.

        Returns:
            str: The string representation of the enumeration value
        """
        return self.value

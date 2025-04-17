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
    """Type settings enumeration for forest thinning application.

    This enumeration class defines different types of settings used in the forest thinning
    application, including area, breed, condition, and graphic settings.

    Attributes:
        AREA (str): Region or area setting, represented as "Регион"
        BREED (str): Tree breed setting, represented as "Порода"
        CONDITION (str): Conditions setting, represented as "Условия"
        GRAPHIC (str): Graph setting, represented as "График"
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

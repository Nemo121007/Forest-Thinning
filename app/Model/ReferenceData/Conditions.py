"""Module for managing condition data in a reference data system.

This module provides the Conditions class, which extends ReferenceEntity to manage condition
data, including names and codes, with support for transactions and integration with graphics
data for usage tracking and file name updates.
"""

from .ReferenceEntity import ReferenceEntity
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .Graphics import Graphics


class Conditions(ReferenceEntity):
    """A class for managing condition data, extending ReferenceEntity.

    Handles storage, manipulation, and validation of condition data (names and codes), with
    transactional support for operations like adding, deleting, and updating conditions.
    Integrates with a Graphics entity to track usage and update associated graphic file names
    when conditions are modified.

    Attributes:
        _graphics (Graphics, optional): The Graphics entity for tracking condition usage and
            updating file names.
    """

    def __init__(self, graphics: Optional["Graphics"] = None) -> None:
        """Initialize the Conditions entity.

        Sets up the base ReferenceEntity with the 'conditions' data key and stores the
        Graphics entity for usage tracking.

        Args:
            graphics (Graphics, optional): The Graphics entity to associate with conditions.
                Defaults to None.
        """
        super().__init__("conditions")
        self._graphics = graphics

    def initialize(self, data: dict) -> None:
        """Initialize condition data from a dictionary.

        Loads condition data from the provided dictionary and sets up usage tracking.

        Args:
            data (dict): A dictionary containing condition data under the 'conditions' key.

        Returns:
            None
        """
        self._data = dict(data.get(self._data_key, {}))
        self._used = {key: False for key in self._data.keys()}

    def save_data(self, reference_data: dict) -> None:
        """Save condition data to a reference dictionary.

        Stores the current condition data in the provided dictionary under the 'conditions'
        key.

        Args:
            reference_data (dict): The dictionary to store condition data.

        Returns:
            None
        """
        reference_data[self._data_key] = self._data

    def add_condition(self, name: str, code: str) -> None:
        """Add a new condition with the specified name and code.

        Validates that the name and code do not already exist before adding the condition
        within a transaction.

        Args:
            name (str): The name of the new condition.
            code (str): The code of the new condition.

        Returns:
            None

        Raises:
            ValueError: If the condition name or code already exists.
        """
        if name in self._data:
            raise ValueError(f"Condition '{name}' already exists")
        if code in self._data.values():
            raise ValueError(f"Code condition '{code}' already exists")
        with self.transaction():
            self._data[name] = code
            self._used[name] = False

    def delete_condition(self, name: str) -> None:
        """Delete an existing condition.

        Ensures the condition is not used before deleting it within a transaction.

        Args:
            name (str): The name of the condition to delete.

        Returns:
            None

        Raises:
            ValueError: If the condition is used in graphics and cannot be deleted.
        """
        if self._used[name]:
            raise ValueError("Cannot delete used condition")
        with self.transaction():
            del self._data[name]
            del self._used[name]

    def update_condition(self, old_name: str, name: str, code: str) -> None:
        """Update an existing condition's name and code.

        Validates the new name and code, updates the condition within a transaction, and
        updates associated graphic file names if a Graphics entity is present.

        Args:
            old_name (str): The current name of the condition.
            name (str): The new name for the condition.
            code (str): The new code for the condition.

        Returns:
            None

        Raises:
            ValueError: If the old name does not exist, the new name already exists (unless
                unchanged), or the new code already exists (unless unchanged).
        """
        if old_name not in self._data:
            raise ValueError("Old condition name does not exist")
        if old_name != name and name in self._data:
            raise ValueError("New condition name already exists")
        if code != self._data[old_name] and code in self._data.values():
            raise ValueError("New code already exists")
        with self.transaction():
            old_value = self._data[old_name]
            used_status = self._used[old_name]
            del self._data[old_name]
            del self._used[old_name]
            self._data[name] = code
            self._used[name] = used_status
            if self._graphics:
                for (area, breed, condition), value in list(self._graphics._data.items()):
                    if condition == old_name:
                        old_file_name = (
                            f"{self._graphics._areas.get_value(area)}_"
                            + f"{self._graphics._breeds.get_value(breed)}_"
                            + f"{old_value}"
                        )
                        new_file_name = (
                            f"{self._graphics._areas.get_value(area)}_"
                            + f"{self._graphics._breeds.get_value(breed)}_"
                            + f"{code}"
                        )
                        self._graphics.update_name_file_graphic(old_name=old_file_name, new_name=new_file_name)
                        del self._graphics._data[(area, breed, old_name)]
                        self._graphics._data[(area, breed, name)] = value

    def get_value(self, name: str) -> str:
        """Retrieve the code associated with a condition.

        Args:
            name (str): The name of the condition.

        Returns:
            str: The code of the condition, or None if the condition does not exist.
        """
        return self._data.get(name)

    def exist_name(self, name: str) -> bool:
        """Check if a condition name exists.

        Args:
            name (str): The name to check.

        Returns:
            bool: True if the condition name exists, False otherwise.
        """
        return name in self._data

    def exist_code(self, code: str) -> bool:
        """Check if a condition code exists.

        Args:
            code (str): The code to check.

        Returns:
            bool: True if the condition code exists, False otherwise.
        """
        return code in self._data.values()

    def get_list_available(self, area: str = None, breed: str = None) -> list[str]:
        """Retrieve a list of conditions not used in graphics for the given area and breed.

        Args:
            area (str, optional): The area to filter conditions. Defaults to None.
            breed (str, optional): The breed to filter conditions. Defaults to None.

        Returns:
            list[str]: A list of condition names not used in graphics matching the filters.
        """
        result = []
        for condition in self._data.keys():
            for area_graphic, breed_graphic, condition_graphic in self._graphics._data.keys():
                if (
                    condition == condition_graphic
                    and (area is None or area_graphic == area)
                    and (breed is None or breed_graphic == breed)
                ):
                    continue
            result.append(condition)
        return result

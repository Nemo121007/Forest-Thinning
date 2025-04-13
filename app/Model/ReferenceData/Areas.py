"""Module for managing area data in a reference data system.

This module provides the Areas class, which extends ReferenceEntity to manage area data,
including names and codes, with support for transactions and integration with graphics data
for usage tracking and file name updates.
"""

from .ReferenceEntity import ReferenceEntity
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .Graphics import Graphics


class Areas(ReferenceEntity):
    """A class for managing area data, extending ReferenceEntity.

    Handles storage, manipulation, and validation of area data (names and codes), with
    transactional support for operations like adding, deleting, and updating areas. Integrates
    with a Graphics entity to track usage and update associated graphic file names when areas
    are modified.

    Attributes:
        _graphics (Graphics, optional): The Graphics entity for tracking area usage and
            updating file names.
    """

    def __init__(self, graphics: Optional["Graphics"] = None) -> None:
        """Initialize the Areas entity.

        Sets up the base ReferenceEntity with the 'areas' data key and stores the Graphics
        entity for usage tracking.

        Args:
            graphics (Graphics, optional): The Graphics entity to associate with areas.
                Defaults to None.
        """
        super().__init__("areas")
        self._graphics = graphics

    def initialize(self, data: dict) -> None:
        """Initialize area data from a dictionary.

        Loads area data from the provided dictionary and sets up usage tracking.

        Args:
            data (dict): A dictionary containing area data under the 'areas' key.

        Returns:
            None
        """
        self._data = dict(data.get(self._data_key, {}))
        self._used = {key: False for key in self._data.keys()}

    def save_data(self, reference_data: dict) -> None:
        """Save area data to a reference dictionary.

        Stores the current area data in the provided dictionary under the 'areas' key.

        Args:
            reference_data (dict): The dictionary to store area data.

        Returns:
            None
        """
        reference_data[self._data_key] = self._data

    def add_area(self, name: str, code: str) -> None:
        """Add a new area with the specified name and code.

        Validates that the name and code do not already exist before adding the area within
        a transaction.

        Args:
            name (str): The name of the new area.
            code (str): The code of the new area.

        Returns:
            None

        Raises:
            ValueError: If the area name or code already exists.
        """
        if name in self._data:
            raise ValueError(f"Area '{name}' already exists")
        if code in self._data.values():
            raise ValueError(f"Code area '{code}' already exists")
        with self.transaction():
            self._data[name] = code
            self._used[name] = False

    def delete_area(self, name: str) -> None:
        """Delete an existing area.

        Ensures the area is not used before deleting it within a transaction.

        Args:
            name (str): The name of the area to delete.

        Returns:
            None

        Raises:
            ValueError: If the area is used in graphics and cannot be deleted.
        """
        if self._used[name]:
            raise ValueError("Cannot delete used area")
        with self.transaction():
            del self._data[name]
            del self._used[name]

    def update_area(self, old_name: str, name: str, code: str) -> None:
        """Update an existing area's name and code.

        Validates the new name and code, updates the area within a transaction, and
        updates associated graphic file names if a Graphics entity is present.

        Args:
            old_name (str): The current name of the area.
            name (str): The new name for the area.
            code (str): The new code for the area.

        Returns:
            None

        Raises:
            ValueError: If the old name does not exist, the new name already exists (unless
                unchanged), or the new code already exists (unless unchanged).
        """
        if old_name not in self._data:
            raise ValueError("Old area name does not exist")
        if old_name != name and name in self._data:
            raise ValueError("New area name already exists")
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
                    if area == old_name:
                        old_file_name = (
                            f"{old_value}_"
                            + f"{self._graphics._breeds.get_value(breed)}_"
                            + f"{self._graphics._conditions.get_value(condition)}"
                        )
                        new_file_name = (
                            f"{code}_"
                            + f"{self._graphics._breeds.get_value(breed)}_"
                            + f"{self._graphics._conditions.get_value(condition)}"
                        )
                        self._graphics.update_name_file_graphic(old_name=old_file_name, new_name=new_file_name)
                        del self._graphics._data[(old_name, breed, condition)]
                        self._graphics._data[(name, breed, condition)] = value

    def get_value(self, name: str) -> str:
        """Retrieve the code associated with an area.

        Args:
            name (str): The name of the area.

        Returns:
            str: The code of the area, or None if the area does not exist.
        """
        return self._data.get(name)

    def exist_name(self, name: str) -> bool:
        """Check if an area name exists.

        Args:
            name (str): The name to check.

        Returns:
            bool: True if the area name exists, False otherwise.
        """
        return name in self._data

    def exist_code(self, code: str) -> bool:
        """Check if an area code exists.

        Args:
            code (str): The code to check.

        Returns:
            bool: True if the area code exists, False otherwise.
        """
        return code in self._data.values()

    def get_list_available(self, breed: str = None, condition: str = None) -> list[str]:
        """Retrieve a list of areas not used in graphics for the given breed and condition.

        Args:
            breed (str, optional): The breed to filter areas. Defaults to None.
            condition (str, optional): The condition to filter areas. Defaults to None.

        Returns:
            list[str]: A list of area names not used in graphics matching the filters.
        """
        result = []
        for area in self._data.keys():
            for area_graphic, breed_graphic, condition_graphic in self._graphics._data.keys():
                if (
                    area == area_graphic
                    and (breed is None or breed_graphic == breed)
                    and (condition is None or condition_graphic == condition)
                ):
                    continue
            result.append(area)
        return result

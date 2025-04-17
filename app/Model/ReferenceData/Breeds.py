"""Module for managing breed data in a reference data system.

This module provides the Breeds class, which extends ReferenceEntity to manage breed data,
including names, codes, and age thinning values, with support for transactions and
integration with graphics data for usage tracking and file name updates.
"""

from .ReferenceEntity import ReferenceEntity
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .Graphics import Graphics


class Breeds(ReferenceEntity):
    """A class for managing breed data, extending ReferenceEntity.

    Handles storage, manipulation, and validation of breed data (names, codes, age thinning,
    and age thinning save values), with transactional support for operations like adding,
    deleting, and updating breeds. Integrates with a Graphics entity to track usage and
    update associated graphic file names when breeds are modified.

    Attributes:
        _graphics (Graphics, optional): The Graphics entity for tracking breed usage and
            updating file names.
    """

    def __init__(self, graphics: Optional["Graphics"] = None):
        """Initialize the Breeds entity.

        Sets up the base ReferenceEntity with the 'breeds' data key and stores the Graphics
        entity for usage tracking.

        Args:
            graphics (Graphics, optional): The Graphics entity to associate with breeds.
                Defaults to None.
        """
        super().__init__("breeds")
        self._graphics = graphics

    def initialize(self, data: dict):
        """Initialize breed data from a dictionary.

        Loads breed data from the provided dictionary and sets up usage tracking.

        Args:
            data (dict): A dictionary containing breed data under the 'breeds' key.

        Returns:
            None
        """
        self._data = dict(data.get(self._data_key, {}))
        self._used = {key: False for key in self._data.keys()}

    def save_data(self, reference_data: dict):
        """Save breed data to a reference dictionary.

        Stores the current breed data in the provided dictionary under the 'breeds' key.

        Args:
            reference_data (dict): The dictionary to store breed data.

        Returns:
            None
        """
        reference_data[self._data_key] = self._data

    def add_breed(self, name: str, code: str, age_thinning: float, age_thinning_save: float) -> None:
        """Add a new breed with the specified name, code, and age thinning values.

        Validates that the name and code do not already exist before adding the breed within
        a transaction.

        Args:
            name (str): The name of the new breed.
            code (str): The code of the new breed.
            age_thinning (float): The age thinning value for the breed.
            age_thinning_save (float): The age thinning save value for the breed.

        Returns:
            None

        Raises:
            ValueError: If the breed name or code already exists.
        """
        if name in self._data:
            raise ValueError(f"Breed '{name}' already exists")
        if any(breed["value"] == code for breed in self._data.values()):
            raise ValueError(f"Code breed '{code}' already exists")
        with self.transaction():
            self._data[name] = {
                "value": code,
                "age_thinning": age_thinning,
                "age_thinning_save": age_thinning_save,
            }
            self._used[name] = False

    def delete_breed(self, name: str) -> None:
        """Delete an existing breed.

        Ensures the breed is not used before deleting it within a transaction.

        Args:
            name (str): The name of the breed to delete.

        Returns:
            None

        Raises:
            ValueError: If the breed is used in graphics and cannot be deleted.
        """
        if self._used[name]:
            raise ValueError("Cannot delete used breed")
        with self.transaction():
            del self._data[name]
            del self._used[name]

    def update_breed(self, old_name: str, name: str, code: str, age_thinning: float, age_thinning_save: float) -> None:
        """Update an existing breed's name, code, and age thinning values.

        Validates the new name and code, updates the breed within a transaction, and updates
        associated graphic file names if a Graphics entity is present.

        Args:
            old_name (str): The current name of the breed.
            name (str): The new name for the breed.
            code (str): The new code for the breed.
            age_thinning (float): The new age thinning value for the breed.
            age_thinning_save (float): The new age thinning save value for the breed.

        Returns:
            None

        Raises:
            ValueError: If the old name does not exist, the new name already exists (unless
                unchanged), or the new code already exists (unless unchanged).
        """
        if old_name not in self._data:
            raise ValueError("Old breed name does not exist")
        if old_name != name and name in self._data:
            raise ValueError("New breed name already exists")
        if code != self._data[old_name]["value"] and any(breed["value"] == code for breed in self._data.values()):
            raise ValueError("New code already exists")
        with self.transaction():
            old_value = self._data[old_name]["value"]
            used_status = self._used[old_name]
            del self._data[old_name]
            del self._used[old_name]
            self._data[name] = {
                "value": code,
                "age_thinning": age_thinning,
                "age_thinning_save": age_thinning_save,
            }
            self._used[name] = used_status
            if self._graphics:
                for (area, breed, condition), value in list(self._graphics._data.items()):
                    if breed == old_name:
                        old_file_name = (
                            f"{self._graphics._areas.get_value(area)}_"
                            + f"{old_value}_"
                            + f"{self._graphics._conditions.get_value(condition)}"
                        )
                        new_file_name = (
                            f"{self._graphics._areas.get_value(area)}_"
                            + f"{code}_"
                            + f"{self._graphics._conditions.get_value(condition)}"
                        )
                        self._graphics.rename_graphic(old_name_graphic=old_file_name, new_name_graphic=new_file_name)
                        self._graphics.update_name_file_graphic(old_name=old_file_name, new_name=new_file_name)
                        del self._graphics._data[(area, old_name, condition)]
                        self._graphics._data[(area, name, condition)] = value

    def get_value(self, name: str) -> str | None:
        """Retrieve the code associated with a breed.

        Args:
            name (str): The name of the breed.

        Returns:
            str | None: The code of the breed, or None if the breed does not exist.
        """
        breed = self._data.get(name)
        return breed["value"] if breed else None

    def get_age_thinning(self, name: str) -> float | None:
        """Retrieve the age thinning value for a breed.

        Args:
            name (str): The name of the breed.

        Returns:
            float | None: The age thinning value of the breed, or None if the breed does
                not exist.
        """
        breed = self._data.get(name)
        return breed["age_thinning"] if breed else None

    def get_age_thinning_save(self, name: str) -> float | None:
        """Retrieve the age thinning save value for a breed.

        Args:
            name (str): The name of the breed.

        Returns:
            float | None: The age thinning save value of the breed, or None if the breed
                does not exist.
        """
        breed = self._data.get(name)
        return breed["age_thinning_save"] if breed else None

    def exist_name(self, name: str) -> bool:
        """Check if a breed name exists.

        Args:
            name (str): The name to check.

        Returns:
            bool: True if the breed name exists, False otherwise.
        """
        return name in self._data

    def exist_code(self, code: str) -> bool:
        """Check if a breed code exists.

        Args:
            code (str): The code to check.

        Returns:
            bool: True if the breed code exists, False otherwise.
        """
        return code in self._data.values()

    def get_list_available(self, area: str = None, condition: str = None) -> list[str]:
        """Retrieve a list of breeds not used in graphics for the given area and condition.

        Args:
            area (str, optional): The area to filter breeds. Defaults to None.
            condition (str, optional): The condition to filter breeds. Defaults to None.

        Returns:
            list[str]: A list of breed names not used in graphics matching the filters.
        """
        result = []
        for breed in self._data.keys():
            for area_graphic, breed_graphic, condition_graphic in self._graphics._data.keys():
                if (
                    breed == breed_graphic
                    and (area is None or area_graphic == area)
                    and (condition is None or condition_graphic == condition)
                ):
                    continue
            result.append(breed)
        return result

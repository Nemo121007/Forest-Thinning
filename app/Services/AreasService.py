"""Module for managing area-related data in a reference data system.

This module provides the AreasService class, which interacts with a ReferenceDataManager
to perform operations on area data, including retrieval, addition, deletion, updating,
and validation of areas used in graphics.
"""

from .ReferenceDataManagerService import ReferenceDataManagerServices


class AreasService:
    """A service class for managing area data.

    Provides methods to interact with area data through a ReferenceDataManager instance,
    including listing areas, checking usage, validating names and codes, and performing
    CRUD operations. Saves changes to persistent storage
    via the manager.

    Attributes:
        manager (ReferenceDataManager): The reference data manager instance.
        areas (object): The area data entity managed by ReferenceDataManager.
        graphics (object): The graphics data entity managed by ReferenceDataManager.
    """

    def __init__(self):
        """Initialize the AreasService.

        Sets up the service by retrieving the ReferenceDataManager instance and accessing
        its areas and graphics entities.
        """
        self.manager = ReferenceDataManagerServices().manager
        self.areas = self.manager.get_areas()
        self.graphics = self.manager.get_graphics()

    def get_list_areas(self) -> list[str]:
        """Retrieve a list of all area names.

        Returns:
            list[str]: A list of area names.

        Raises:
            Exception: If an error occurs while retrieving the list of areas.
        """
        try:
            result = self.areas.get_list()
            return result
        except Exception as e:
            raise Exception(f"Error get list: {e}")

    def get_list_allowed_areas(self, breed: str = None, condition: str = None) -> list[str]:
        """Retrieve a list of all area names.

        Returns:
            list[str]: A list of area names.

        Raises:
            Exception: If an error occurs while retrieving the list of areas.
        """
        try:
            result = self.graphics.get_list_allowed_areas(breed=breed, condition=condition)
            return result
        except Exception as e:
            raise (f"Error get list allowed area: {e}")

    def get_list_used_areas(self) -> list[tuple[str, bool]]:
        """Retrieve a list of areas allowed for a given breed and condition.

        Args:
            breed (str, optional): The breed to filter allowed areas. Defaults to None.
            condition (str, optional): The condition to filter allowed areas. Defaults to None.

        Returns:
            list[tuple[str, bool]]: A list of allowed area names.

        Raises:
            Exception: If an error occurs while retrieving the list of allowed areas.
        """
        try:
            result = self.areas.get_list_used()
            return result
        except Exception as e:
            raise Exception(f"Error get list allowed area {e}")

    def check_used_area(self, name: str) -> bool:
        """Check if an area is used in graphics.

        Args:
            name (str): The name of the area to check.

        Returns:
            bool: True if the area is used, False otherwise.

        Raises:
            Exception: If an error occurs while checking the area's usage.
        """
        try:
            result = self.areas.check_used(name=name)
            return result
        except Exception as e:
            raise Exception(f"Error check used area {e}")

    def get_value_area(self, name: str) -> str:
        """Retrieve the code associated with an area.

        Args:
            name (str): The name of the area.

        Returns:
            str: The code of the area.

        Raises:
            Exception: If an error occurs while retrieving the area's code.
        """
        try:
            result = self.areas.get_value(name=name)
            return result
        except Exception as e:
            raise Exception(f"Error get value area {e}")

    def exist_name_area(self, name: str) -> bool:
        """Check if an area name already exists.

        Args:
            name (str): The name to check.

        Returns:
            bool: True if the area name exists, False otherwise.

        Raises:
            Exception: If an error occurs while checking the area name's existence.
        """
        try:
            result = self.areas.exist_name(name=name)
            return result
        except Exception as e:
            raise Exception(f"Error exist name area {e}")

    def exist_code_area(self, code: str) -> bool:
        """Check if an area code already exists.

        Args:
            code (str): The code to check.

        Returns:
            bool: True if the area code exists, False otherwise.

        Raises:
            Exception: If an error occurs while checking the area code's existence.
        """
        try:
            result = self.areas.exist_code(code=code)
            return result
        except Exception as e:
            raise Exception(f"Error exist code area {e}")

    def add_area(self, name: str, code: str) -> None:
        """Add a new area.

        Adds an area with the specified name and code, then saves the changes to persistent
        storage.

        Args:
            name (str): The name of the new area.
            code (str): The code of the new area.

        Returns:
            None

        Raises:
            Exception: If an error occurs while adding the area.
        """
        try:
            self.areas.add_area(name=name, code=code)
            self.manager.save_data()
        except Exception as e:
            raise Exception(f"Error add area {e}")

    def delete_area(self, name: str) -> None:
        """Delete an existing area.

        Removes the specified area and saves the changes to persistent storage.

        Args:
            name (str): The name of the area to delete.

        Returns:
            None

        Raises:
            Exception: If an error occurs while deleting the area.
        """
        try:
            self.areas.delete_area(name=name)
            self.manager.save_data()
        except Exception as e:
            raise Exception(f"Error delete area {e}")

    def update_area(self, old_name: str, name: str, code: str) -> None:
        """Update an existing area.

        Updates the name and code of the specified area and saves the changes to persistent
        storage.

        Args:
            old_name (str): The current name of the area to update.
            name (str): The new name for the area.
            code (str): The new code for the area.

        Returns:
            None

        Raises:
            Exception: If an error occurs while updating the area.
        """
        try:
            self.areas.update_area(old_name=old_name, name=name, code=code)
            self.manager.save_data()
        except Exception as e:
            raise Exception(f"Error update area {e}")

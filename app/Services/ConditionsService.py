"""Module for managing condition-related data in a reference data system.

This module provides the ConditionsService class, which interacts with a ReferenceDataManager
to perform operations on condition data, including retrieval, addition, deletion, updating,
and validation of conditions used in graphics.
"""

from .ReferenceDataManagerService import ReferenceDataManagerServices


class ConditionsService:
    """A service class for managing condition data.

    Provides methods to interact with condition data through a ReferenceDataManager instance,
    including listing conditions, checking usage, validating names and codes, and performing
    CRUD operations. Saves changes to persistent storage
    via the manager.

    Attributes:
        manager (ReferenceDataManager): The reference data manager instance.
        conditions (object): The condition data entity managed by ReferenceDataManager.
        graphics (object): The graphics data entity managed by ReferenceDataManager.
    """

    def __init__(self) -> None:
        """Initialize the ConditionsService.

        Sets up the service by retrieving the ReferenceDataManager instance and accessing
        its conditions and graphics entities.
        """
        self.manager = ReferenceDataManagerServices().manager
        self.conditions = self.manager.get_conditions()
        self.graphics = self.manager.get_graphics()

    def get_list_conditions(self) -> list[str]:
        """Retrieve a list of all condition names.

        Returns:
            list: A list of condition names.

        Raises:
            Exception: If an error occurs while retrieving the list of conditions.
        """
        try:
            result = self.conditions.get_list()
            return result
        except Exception as e:
            raise Exception(f"Error get list condition {str(e)}")

    def get_list_allowed_condition(self, area: str = None, breed: str = None) -> list[bool]:
        """Retrieve a list of conditions allowed for a given area and breed.

        Args:
            area (str, optional): The area to filter allowed conditions. Defaults to None.
            breed (str, optional): The breed to filter allowed conditions. Defaults to None.

        Returns:
            list: A list of allowed condition names.

        Raises:
            Exception: If an error occurs while retrieving the list of allowed conditions.
        """
        try:
            result = self.graphics.get_list_allowed_conditions(area=area, breed=breed)
            return result
        except Exception as e:
            raise Exception(f"Error get list allowed condition {str(e)}")

    def get_list_used_condition(self) -> list[tuple[str, bool]]:
        """Retrieve a list of conditions with their usage status.

        Returns:
            list[tuple[str, bool]]: A list of tuples, each containing a condition name and
                its usage status (True if used, False otherwise).

        Raises:
            Exception: If an error occurs while retrieving the list of used conditions.
        """
        try:
            result = self.conditions.get_list_used()
            return result
        except Exception as e:
            raise Exception(f"Error get list allowed condition {str(e)}")

    def check_used_condition(self, name: str) -> bool:
        """Check if a condition is used in graphics.

        Args:
            name (str): The name of the condition to check.

        Returns:
            bool: True if the condition is used, False otherwise.

        Raises:
            Exception: If an error occurs while checking the condition's usage.
        """
        try:
            result = self.conditions.check_used(name=name)
            return result
        except Exception as e:
            raise Exception(f"Error check used condition {str(e)}")

    def get_value_condition(self, name: str) -> str:
        """Retrieve the code associated with a condition.

        Args:
            name (str): The name of the condition.

        Returns:
            str: The code of the condition.

        Raises:
            Exception: If an error occurs while retrieving the condition's code.
        """
        try:
            result = self.conditions.get_value(name=name)
            return result
        except Exception as e:
            raise Exception(f"Error get value condition {str(e)}")

    def exist_name_condition(self, name: str) -> bool:
        """Check if a condition name already exists.

        Args:
            name (str): The name to check.

        Returns:
            bool: True if the condition name exists, False otherwise.

        Raises:
            Exception: If an error occurs while checking the condition name's existence.
        """
        try:
            result = self.conditions.exist_name(name=name)
            return result
        except Exception as e:
            raise Exception(f"Error exist name condition {str(e)}")

    def exist_code_condition(self, code: str) -> bool:
        """Check if a condition code already exists.

        Args:
            code (str): The code to check.

        Returns:
            bool: True if the condition code exists, False otherwise.

        Raises:
            Exception: If an error occurs while checking the condition code's existence.
        """
        try:
            result = self.conditions.exist_code(code=code)
            return result
        except Exception as e:
            raise Exception(f"Error exist code condition {str(e)}")

    def add_condition(self, name: str, code: str) -> None:
        """Add a new condition.

        Adds a condition with the specified name and code, then saves the changes to
        persistent storage.

        Args:
            name (str): The name of the new condition.
            code (str): The code of the new condition.

        Returns:
            None

        Raises:
            Exception: If an error occurs while adding the condition.
        """
        try:
            self.conditions.add_condition(name=name, code=code)
            self.manager.save_data()
        except Exception as e:
            raise Exception(f"Error add condition {str(e)}")

    def delete_condition(self, name: str) -> None:
        """Delete an existing condition.

        Removes the specified condition and saves the changes to persistent storage.

        Args:
            name (str): The name of the condition to delete.

        Returns:
            None

        Raises:
            Exception: If an error occurs while deleting the condition.
        """
        try:
            self.conditions.delete_condition(name=name)
            self.manager.save_data()
        except Exception as e:
            raise Exception(f"Error delete condition {str(e)}")

    def update_condition(self, old_name: str, name: str, code: str) -> None:
        """Update an existing condition.

        Updates the name and code of the specified condition and saves the changes to
        persistent storage.

        Args:
            old_name (str): The current name of the condition to update.
            name (str): The new name for the condition.
            code (str): The new code for the condition.

        Returns:
            None

        Raises:
            Exception: If an error occurs while updating the condition.
        """
        try:
            self.conditions.update_condition(old_name=old_name, name=name, code=code)
            self.manager.save_data()
        except Exception as e:
            raise Exception(f"Error update condition {str(e)}")

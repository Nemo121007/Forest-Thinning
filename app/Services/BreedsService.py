"""Module for managing breed-related data in a reference data system.

This module provides the BreedsService class, which interacts with a ReferenceDataManager
to perform operations on breed data, including retrieval, addition, deletion, updating,
and validation of breeds used in graphics, with additional support for age thinning values.
"""

from .ReferenceDataManagerService import ReferenceDataManagerServices


class BreedsService:
    """A service class for managing breed data.

    Provides methods to interact with breed data through a ReferenceDataManager instance,
    including listing breeds, checking usage, validating names and codes, retrieving age
    thinning values, and performing CRUD operations (create, read, update, delete). Saves
    changes to persistent storage via the manager.

    Attributes:
        manager (ReferenceDataManager): The reference data manager instance.
        breeds (object): The breed data entity managed by ReferenceDataManager.
        graphics (object): The graphics data entity managed by ReferenceDataManager.
    """

    def __init__(self) -> None:
        """Initialize the BreedsService.

        Sets up the service by retrieving the ReferenceDataManager instance and accessing
        its breeds and graphics entities.
        """
        self.manager = ReferenceDataManagerServices().manager
        self.breeds = self.manager.get_breeds()
        self.graphics = self.manager.get_graphics()

    def get_list_breeds(self) -> list[str]:
        """Retrieve a list of all breed names.

        Returns:
            list: A list of breed names.

        Raises:
            Exception: If an error occurs while retrieving the list of breeds.
        """
        try:
            result = self.breeds.get_list()
            return result
        except Exception as e:
            raise Exception(f"Error get list breeds {e}")

    def get_list_allowed_breeds(self, area: str = None, condition: str = None) -> list[str]:
        """Retrieve a list of breeds allowed for a given area and condition.

        Args:
            area (str, optional): The area to filter allowed breeds. Defaults to None.
            condition (str, optional): The condition to filter allowed breeds. Defaults to None.

        Returns:
            list: A list of allowed breed names.

        Raises:
            Exception: If an error occurs while retrieving the list of allowed breeds.
        """
        try:
            result = self.graphics.get_list_allowed_breeds(area=area, condition=condition)
            return result
        except Exception as e:
            raise Exception(f"Error get list allowed breeds {e}")

    def get_list_used_breeds(self) -> list[tuple[str, bool]]:
        """Retrieve a list of breeds with their usage status.

        Returns:
            list[tuple[str, bool]]: A list of tuples, each containing a breed name and
                its usage status (True if used, False otherwise).

        Raises:
            Exception: If an error occurs while retrieving the list of used breeds.
        """
        try:
            result = self.breeds.get_list_used()
            return result
        except Exception as e:
            raise Exception(f"Error get list breeds used {e}")

    def check_used_breed(self, name: str) -> bool:
        """Check if a breed is used in graphics.

        Args:
            name (str): The name of the breed to check.

        Returns:
            bool: True if the breed is used, False otherwise.

        Raises:
            Exception: If an error occurs while checking the breed's usage.
        """
        try:
            result = self.breeds.check_used(name=name)
            return result
        except Exception as e:
            raise Exception(f"Error check used name {e}")

    def get_value_breed(self, name: str) -> str:
        """Retrieve the code associated with a breed.

        Args:
            name (str): The name of the breed.

        Returns:
            str: The code of the breed.

        Raises:
            Exception: If an error occurs while retrieving the breed's code.
        """
        try:
            result = self.breeds.get_value(name=name)
            return result
        except Exception as e:
            raise Exception(f"Error get value breed {e}")

    def get_age_thinning_breed(self, name: str) -> float:
        """Retrieve the age thinning value for a breed.

        Args:
            name (str): The name of the breed.

        Returns:
            float: The age thinning value of the breed.

        Raises:
            Exception: If an error occurs while retrieving the breed's age thinning value.
        """
        try:
            result = self.breeds.get_age_thinning(name=name)
            return result
        except Exception as e:
            raise Exception(f"Error get value breed {e}")

    def get_age_thinning_save_breed(self, name: str) -> float:
        """Retrieve the age thinning save value for a breed.

        Args:
            name (str): The name of the breed.

        Returns:
            float: The age thinning save value of the breed.

        Raises:
            Exception: If an error occurs while retrieving the breed's age thinning save value.
        """
        try:
            result = self.breeds.get_age_thinning_save(name=name)
            return result
        except Exception as e:
            raise Exception(f"Error get value breed {e}")

    def exist_name_breed(self, name: str) -> bool:
        """Check if a breed name already exists.

        Args:
            name (str): The name to check.

        Returns:
            bool: True if the breed name exists, False otherwise.

        Raises:
            Exception: If an error occurs while checking the breed name's existence.
        """
        try:
            result = self.breeds.exist_name(name=name)
            return result
        except Exception as e:
            raise Exception(f"Error exist name breed {e}")

    def exist_code_breed(self, code: str) -> bool:
        """Check if a breed code already exists.

        Args:
            code (str): The code to check.

        Returns:
            bool: True if the breed code exists, False otherwise.

        Raises:
            Exception: If an error occurs while checking the breed code's existence.
        """
        try:
            result = self.breeds.exist_code(code=code)
            return result
        except Exception as e:
            raise Exception(f"Error exist code breed {e}")

    def add_breed(
        self,
        name: str,
        code: str,
        age_thinning: float,
        age_thinning_save: float,
    ) -> None:
        """Add a new breed.

        Adds a breed with the specified name, code, and age thinning values, then saves
        the changes to persistent storage.

        Args:
            name (str): The name of the new breed.
            code (str): The code of the new breed.
            age_thinning (float): The age thinning value for the breed.
            age_thinning_save (float): The age thinning save value for the breed.

        Returns:
            None

        Raises:
            Exception: If an error occurs while adding the breed.
        """
        try:
            self.breeds.add_breed(
                name=name,
                code=code,
                age_thinning=age_thinning,
                age_thinning_save=age_thinning_save,
            )
            self.manager.save_data()
        except Exception as e:
            raise Exception(f"Error add breed {e}")

    def delete_breed(self, name: str) -> None:
        """Delete an existing breed.

        Removes the specified breed and saves the changes to persistent storage.

        Args:
            name (str): The name of the breed to delete.

        Returns:
            None

        Raises:
            Exception: If an error occurs while deleting the breed.
        """
        try:
            self.breeds.delete_breed(name=name)
            self.manager.save_data()
        except Exception as e:
            raise Exception(f"Error delete breed {e}")

    def update_breed(self, old_name: str, name: str, code: str, age_thinning: float, age_thinning_save: float) -> None:
        """Update an existing breed.

        Updates the name, code, and age thinning values of the specified breed and saves
        the changes to persistent storage.

        Args:
            old_name (str): The current name of the breed to update.
            name (str): The new name for the breed.
            code (str): The new code for the breed.
            age_thinning (float): The new age thinning value for the breed.
            age_thinning_save (float): The new age thinning save value for the breed.

        Returns:
            None

        Raises:
            Exception: If an error occurs while updating the breed.
        """
        try:
            self.breeds.update_breed(
                old_name=old_name,
                name=name,
                code=code,
                age_thinning=age_thinning,
                age_thinning_save=age_thinning_save,
            )
            self.manager.save_data()
        except Exception as e:
            raise Exception(f"Error update breed {e}")

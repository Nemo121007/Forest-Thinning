"""A class for managing and maintaining reference data for forest management operations.

This class provides a comprehensive system for managing reference data related to forest areas,
tree breeds, and their conditions. It implements singleton pattern through class-level storage
and provides transaction-safe operations for data manipulation.

The class manages several types of reference data:
    - Areas: Geographic or administrative forest areas
    - Breeds: Types of trees
    - Conditions: States or conditions of forest areas
    - Graphics: Visual representations of forest data

Key Features:
    - Thread-safe transactions for data operations
    - Persistent storage using JSON format
    - Automatic data initialization and saving
    - Usage tracking for all reference elements
    - Validation of data integrity
    - File management for associated graphic files

Class Variables:
    _private_areas (dict): Storage for area definitions
    _private_breeds (dict): Storage for breed definitions
    _private_conditions (dict): Storage for condition definitions
    _private_graphics (dict): Storage for graphic file references
    _used_areas (dict): Tracking usage of areas
    _used_breeds (dict): Tracking usage of breeds
    _used_conditions (dict): Tracking usage of conditions
    _flag_initialize (bool): Initialization status flag

Note:
    All data modifications are performed within transactions to ensure data consistency.
    The class automatically manages the persistence of data to disk storage.
"""

from app.background_information.Paths import Paths
import json
import os
from pathlib import Path
import shutil
from contextlib import contextmanager


class ReferenceData:
    """A class for managing and maintaining reference data for forest management operations.

    This class provides a comprehensive system for managing reference data related to forest areas,
    tree breeds, and their conditions. It implements singleton pattern through class-level storage
    and provides transaction-safe operations for data manipulation.
    The class manages several types of reference data:
    - Areas: Geographic or administrative forest areas
    - Breeds: Types of trees
    - Conditions: States or conditions of forest areas
    - Graphics: Visual representations of forest data
    Key Features:
        - Thread-safe transactions for data operations
        - Persistent storage using JSON format
        - Automatic data initialization and saving
        - Usage tracking for all reference elements
        - Validation of data integrity
        - File management for associated graphic files
    Class Variables:
        _private_areas (dict): Storage for area definitions
        _private_breeds (dict): Storage for breed definitions
        _private_conditions (dict): Storage for condition definitions
        _private_graphics (dict): Storage for graphic file references
        _used_areas (dict): Tracking usage of areas
        _used_breeds (dict): Tracking usage of breeds
        _used_conditions (dict): Tracking usage of conditions
        _flag_initialize (bool): Initialization status flag
        All data modifications are performed within transactions to ensure data consistency.
        The class automatically manages the persistence of data to disk storage.
    """

    _private_areas = {}
    _private_breeds = {}
    _private_conditions = {}
    _private_graphics = {}
    _used_areas = {}
    _used_breeds = {}
    _used_conditions = {}
    _flag_initialize = False

    @contextmanager
    def transaction():
        """A context manager decorator that handles transactions for reference data operations.

        This decorator ensures atomicity of operations with reference data. If any exception occurs
        during the execution of the decorated function, it rolls back to the last saved state by
        reinitializing the reference data.

        Yields:
            None: Yields control to the decorated function.

        Raises:
            Exception: Re-raises any exception that occurs during the execution of the decorated
                function after performing rollback operations.
        """
        try:
            yield
            ReferenceData.save_data()
        except Exception as e:
            ReferenceData.initialize_reference_data()  # Откат к последнему сохраненному состоянию
            raise e

    @staticmethod
    def initialize_reference_data():
        """Initializes reference data from a JSON file or creates new empty data if the file doesn't exist.

        This method reads reference data from a JSON file and populates class variables with areas, breeds,
        conditions, and graphics information. If the file doesn't exist, it creates empty data structures
        and saves them to a new file.
        The method performs the following operations:
        1. Loads data from the JSON file if it exists
        2. Initializes private dictionaries for areas, breeds, and conditions
        3. Sets usage flags for all elements to False
        4. Processes graphics data by splitting keys into area, breed, and condition components
        5. Creates empty data structures if the file doesn't exist

        Returns:
            None

        Side Effects:
            - Modifies class variables: _private_areas, _private_breeds, _private_conditions,
              _used_areas, _used_breeds, _used_conditions, _private_graphics
            - Sets _flag_initialize to True
            - Refreshes used elements
            - May create a new JSON file if it doesn't exist
        """
        if Paths.REFERENCE_DATA.exists():
            with open(Paths.REFERENCE_DATA, encoding="utf-8") as file:
                try:
                    reference_data = dict(json.load(file))
                except Exception:
                    reference_data = dict()
            if reference_data.get("areas"):
                ReferenceData._private_areas = dict(reference_data.get("areas"))
            else:
                ReferenceData._private_areas = dict()
            if reference_data.get("breeds"):
                ReferenceData._private_breeds = dict(reference_data.get("breeds"))
            else:
                ReferenceData._private_breeds = dict()
            if reference_data.get("conditions"):
                ReferenceData._private_conditions = dict(reference_data.get("conditions"))
            else:
                ReferenceData._private_conditions = dict()

            for key in ReferenceData._private_areas.keys():
                ReferenceData._used_areas[key] = False
            for key in ReferenceData._private_breeds.keys():
                ReferenceData._used_breeds[key] = False
            for key in ReferenceData._private_conditions.keys():
                ReferenceData._used_conditions[key] = False

            if reference_data.get("graphics"):
                graphics = dict(reference_data.get("graphics"))
            else:
                graphics = {}
            for key, value in dict(graphics).items():
                area, breed, condition = str(key).split("_")
                ReferenceData._private_graphics[(area, breed, condition)] = value
        else:
            ReferenceData.save_data()
        ReferenceData._flag_initialize = True
        ReferenceData.refresh_used_element()

    @staticmethod
    def save_data() -> None:
        """Saves the reference data to a JSON file.

        This method stores areas, breeds, conditions, and graphics data in a structured JSON format.
        It creates the necessary directory structure if it doesn't exist and handles the file creation
        and writing operations.
        The graphics data is transformed from a tuple-based key structure to a string-based key
        structure before saving.
        The data is saved with UTF-8 encoding and proper JSON formatting (with indentation).

        Raises:
            Exception: If any error occurs during file operations or JSON dumping process.
        """
        if not Paths.REFERENCE_DATA.exists():
            Paths.REFERENCE_DATA.parent.mkdir(parents=True, exist_ok=True)
            Paths.REFERENCE_DATA.touch()

        graphics = {}
        for (area, breed, condition), value in ReferenceData._private_graphics.items():
            key_str = f"{area}_{breed}_{condition}"
            graphics[key_str] = value

        reference_data = {
            "areas": ReferenceData._private_areas,
            "breeds": ReferenceData._private_breeds,
            "conditions": ReferenceData._private_conditions,
            "graphics": graphics,
        }
        try:
            with open(Paths.REFERENCE_DATA, "w", encoding="utf-8") as file:
                json.dump(reference_data, file, indent=4, ensure_ascii=False)
        except Exception:
            raise

    @staticmethod
    def get_list_areas() -> list:
        """Returns a list of all area names from the reference data.

        This method ensures the reference data is initialized before returning the area names.
        If the data hasn't been initialized yet, it calls the initialization method first.

        Returns:
            list: A list of strings containing all area names from the reference data.
        """
        if not ReferenceData._flag_initialize:
            ReferenceData.initialize_reference_data()
        return list(ReferenceData._private_areas.keys())

    @staticmethod
    def get_list_allowed_areas(breed: str = None, condition: str = None) -> list:
        """Gets a list of unique areas based on specified breed and condition filters.

        This function searches through the private graphics data and returns a list of unique
        areas that match the given breed and/or condition criteria.

        Args:
            breed (str, optional): The tree breed to filter by. If None, all breeds are considered.
            condition (str, optional): The condition to filter by. If None, all conditions are considered.

        Returns:
            list: A list of unique area values that match the specified filters.
        """
        result = []
        for area_current, breed_current, condition_current in ReferenceData._private_graphics.keys():
            if (breed is None or breed == breed_current) and (condition is None or condition == condition_current):
                if area_current not in result:
                    result.append(area_current)
        return result

    @staticmethod
    def get_list_areas_used() -> list:
        """Gets a list of areas that have been used in the calculations.

        Returns:
            list: A list of tuples, where each tuple contains:
                - str: The area key/identifier
                - bool: The usage status of the area (True if used, False if not)
        """
        result = []
        for key in ReferenceData._private_areas.keys():
            result.append((key, ReferenceData._used_areas[key]))
        return result

    @staticmethod
    def check_used_area(name: str) -> bool:
        """Checks if a given area name has been used.

        Args:
            name (str): The name of the area to check.

        Returns:
            bool: True if the area has been used, False otherwise.
        """
        return ReferenceData._used_areas.get(name, False)

    @staticmethod
    def get_value_area(name: str) -> str:
        """Gets the resource area value by its name.

        Args:
            name (str): The name of the resource area.

        Returns:
            str: The value associated with the resource area name. Returns None if the name is not found.
        """
        return ReferenceData._private_areas.get(name)

    @staticmethod
    def exist_name_area(name: str) -> bool:
        """Checks if the specified area name exists in the private areas collection.

        Args:
            name (str): The name of the area to check.

        Returns:
            bool: True if the area name exists in the private areas collection, False otherwise.
        """
        return name in ReferenceData._private_areas

    @staticmethod
    def exist_code_area(code: str) -> bool:
        """Checks if the given code exists in the private areas dictionary.

        Args:
            code (str): The area code to check.

        Returns:
            bool: True if the code exists in the private areas dictionary, False otherwise.
        """
        return code in ReferenceData._private_areas.values()

    @staticmethod
    def add_area(name: str, code: str) -> None:
        """Adds a new area with its code to the reference data.

        Args:
            name (str): The name of the area to be added.
            code (str): The unique code associated with the area.

        Raises:
            ValueError: If the area name already exists in the reference data.
            ValueError: If the area code already exists in the reference data.

        Returns:
            None
        Note:
            This method automatically saves the updated data after adding the new area.
            The area is initially marked as unused in the system.
        """
        if ReferenceData.exist_name_area(name):
            raise ValueError(f"Area '{name}' already exists")
        if ReferenceData.exist_code_area(code):
            raise ValueError(f"Code area'{code}' already exists")
        with ReferenceData.transaction():
            ReferenceData._private_areas[name] = code
            ReferenceData._used_areas[name] = False
        ReferenceData.save_data()

    @staticmethod
    def delete_area(name: str) -> None:
        """Deletes an area from the reference data if it's not currently in use.

        Args:
            name (str): The name of the area to be deleted.

        Raises:
            ValueError: If the area is currently in use (marked as used in _used_areas).

        Note:
            This operation is performed within a transaction and automatically saves
            the updated data after successful deletion.
        """
        if ReferenceData._used_areas[name]:
            raise ValueError("Impossible delete used area")
        with ReferenceData.transaction():
            del ReferenceData._private_areas[name]
            del ReferenceData._used_areas[name]
        ReferenceData.save_data()

    @staticmethod
    def update_area(old_name: str, name: str, code: str) -> None:
        """Updates the area information in the reference data.

        This method updates the name and code of an existing area in the reference data. It also updates
        all related graphics files and maintains the usage status of the area. The operation is performed
        within a transaction to ensure data consistency.

        Args:
            old_name (str): The current name of the area to be updated.
            name (str): The new name for the area.
            code (str): The new code for the area.

        Raises:
            ValueError: If any of these conditions are met:
                - The old_name doesn't exist in the reference data
                - The new name already exists (when changing the name)
                - The new code already exists (when changing both name and code)

        Note:
            This method automatically saves the updated data after successful execution.
        """
        if not ReferenceData.exist_name_area(old_name):
            raise ValueError("Not exist old name area")
        if old_name != name and ReferenceData.exist_name_area(name):
            raise ValueError("Exist name area")
        if (old_name != name and code != ReferenceData._private_areas[old_name]) and (
            ReferenceData.exist_code_area(code=code)
        ):
            raise ValueError("Exist code name area")

        with ReferenceData.transaction():
            old_value = ReferenceData._private_areas[old_name]
            del ReferenceData._private_areas[old_name]

            value_used = ReferenceData._used_areas[old_name]
            del ReferenceData._used_areas[old_name]
            ReferenceData.add_area(name=name, code=code)
            ReferenceData._used_areas[name] = value_used

            for (area, breed, condition), value in list(ReferenceData._private_graphics.items()):
                if area == old_name:
                    ReferenceData.update_name_file_graphic(
                        old_name=f"{old_value}_{ReferenceData.get_value_breed(breed)}_{ReferenceData.get_value_condition(condition)}",
                        new_name=f"{ReferenceData.get_value_area(area)}_{ReferenceData.get_value_breed(breed)}_{ReferenceData.get_value_condition(condition)}",
                    )
                    del ReferenceData._private_graphics[(old_name, breed, condition)]
                    ReferenceData._private_graphics[(name, breed, condition)] = value

        ReferenceData.save_data()

    @staticmethod
    def get_list_breeds() -> list:
        """Gets a list of all available tree breeds.

        Returns:
            list: A list of strings containing tree breed names.

        Note:
            This method automatically initializes reference data if it hasn't been initialized yet.
        """
        if not ReferenceData._flag_initialize:
            ReferenceData.initialize_reference_data()
        return list(ReferenceData._private_breeds.keys())

    @staticmethod
    def get_list_allowed_breeds(area: str = None, condition: str = None) -> list:
        """Gets a list of unique allowed tree breeds based on specified area and condition.

        This function filters through the private graphics data and returns a list of unique
        tree breeds that match the given area and condition criteria.

        Args:
            area (str, optional): The specific area to filter breeds by. If None, includes all areas.
            condition (str, optional): The specific condition to filter breeds by. If None, includes all conditions.

        Returns:
            list: A list of unique tree breed names that match the specified criteria.
        """
        result = []
        for area_current, breed_current, condition_current in ReferenceData._private_graphics.keys():
            if (area is None or area == area_current) and (condition is None or condition == condition_current):
                if breed_current not in result:
                    result.append(breed_current)
        return result

    @staticmethod
    def get_list_breeds_used() -> list:
        """Returns a list of tuples containing breeds and their usage status.

        Returns:
            list: A list of tuples where each tuple contains:
                - str: The breed key/name
                - bool: The usage status of the breed (True if used, False if not).
        """
        result = []
        for key in ReferenceData._private_breeds.keys():
            result.append((key, ReferenceData._used_breeds[key]))
        return result

    @staticmethod
    def check_used_breed(name: str) -> bool:
        """Checks if a tree breed is used in the dataset.

        Args:
            name (str): The name of the tree breed to check.

        Returns:
            bool: True if the breed is used, False otherwise.
        """
        return ReferenceData._used_breeds.get(name, False)

    @staticmethod
    def get_value_breed(name: str) -> str | None:
        """Gets the value associated with a breed name from the private breeds dictionary.

        Args:
            name (str): The name of the breed to look up.

        Returns:
            str | None: The value associated with the breed name if found, None otherwise.
        """
        breed = ReferenceData._private_breeds.get(name)
        return breed["value"] if breed else None

    @staticmethod
    def get_age_thinning_breed(name: str) -> float:
        """Gets the age of thinning for a specific tree breed.

        Args:
            name (str): The name of the tree breed.

        Returns:
            float: The age at which thinning should be performed for the specified breed.
                   Returns None if the breed is not found.
        """
        breed = ReferenceData._private_breeds.get(name)
        return breed["age_thinning"] if breed else None

    @staticmethod
    def get_age_thinning_save_breed(name: str) -> float:
        """Gets the minimum value of age of selected breed when the thinning will save the tree.

        Args:
            name (str): The name of the breed.

        Returns:
            float: The minimum age when thinning will save the breed.
                   Returns None if breed is not found.
        """
        breed = ReferenceData._private_breeds.get(name)
        return breed["age_thinning_save"] if breed else None

    @staticmethod
    def exist_name_breed(name: str) -> bool:
        """Checks if a given breed name exists in the private breeds collection.

        Args:
            name (str): The breed name to check.

        Returns:
            bool: True if the breed name exists in the private breeds collection, False otherwise.
        """
        return name in ReferenceData._private_breeds

    @staticmethod
    def exist_code_breed(code: str) -> bool:
        """Checks if a breed code exists in the private breeds dictionary.

        Args:
            code (str): The breed code to check.

        Returns:
            bool: True if the breed code exists in the private breeds dictionary, False otherwise.
        """
        return any(breed["value"] == code for breed in ReferenceData._private_breeds.values())

    @staticmethod
    def add_breed(
        name: str,
        code: str,
        age_thinning: float,
        age_thinning_save: float,
    ) -> None:
        """Adds a new breed to the reference data.

        This method adds a new breed with specified parameters to the reference data storage.
        The breed must have a unique name and code.

        Args:
            name (str): The name of the breed to add.
            code (str): The unique code identifier for the breed.
            age_thinning (float): The age at which thinning should be performed.
            age_thinning_save (float): The age at which thinning preservation should be performed.

        Raises:
            ValueError: If a breed with the given name or code already exists in the reference data.

        Returns:
            None
        """
        if ReferenceData.exist_name_breed(name):
            raise ValueError(f"Breed '{name}' already exists")
        if ReferenceData.exist_code_breed(code):
            raise ValueError(f"Code breed'{code}' already exists")

        with ReferenceData.transaction():
            ReferenceData._private_breeds[name] = {
                "value": code,
                "age_thinning": age_thinning,
                "age_thinning_save": age_thinning_save,
            }
            ReferenceData._used_breeds[name] = False
        ReferenceData.save_data()

    @staticmethod
    def delete_breed(name: str) -> None:
        """Deletes a breed from reference data if it's not being used.

        Args:
            name (str): Name of the breed to be deleted.

        Raises:
            ValueError: If the breed is currently in use and cannot be deleted.

        Note:
            The method operates within a transaction and automatically saves changes
            to the reference data after successful deletion.
        """
        if ReferenceData._used_breeds[name]:
            raise ValueError("Impossible delete used breed")
        with ReferenceData.transaction():
            del ReferenceData._private_breeds[name]
            del ReferenceData._used_breeds[name]
        ReferenceData.save_data()

    @staticmethod
    def update_breed(old_name: str, name: str, code: str, age_thinning: float, age_thinning_save: float) -> None:
        """Updates the breed information in the reference data.

        Updates an existing breed's information with new values and handles all related data
        updates including used breeds and graphics references.

        Args:
            old_name (str): The current name of the breed to be updated.
            name (str): The new name for the breed.
            code (str): The new code for the breed.
            age_thinning (float): The new age for thinning.
            age_thinning_save (float): The new age for preservation thinning.

        Raises:
            ValueError: If the old_name doesn't exist in the breeds database.
            ValueError: If the new name already exists (when different from old_name).
            ValueError: If the new code already exists (when different from current code).

        Returns:
            None
        Note:
            This method performs a transaction that updates multiple related data structures
                and saves the changes to persistent storage.
        """
        if not ReferenceData.exist_name_breed(name=old_name):
            raise ValueError("Not exist old name breed")
        if name != old_name and ReferenceData.exist_name_breed(name):
            raise ValueError("Exist name breed")
        if ReferenceData.exist_code_breed(code=code) and code != ReferenceData._private_breeds[old_name]["value"]:
            raise ValueError("Exist code breed")

        with ReferenceData.transaction():
            old_value = ReferenceData._private_breeds[old_name]["value"]
            del ReferenceData._private_breeds[old_name]

            value_used = ReferenceData._used_breeds[old_name]
            del ReferenceData._used_breeds[old_name]

            ReferenceData.add_breed(
                name=name, code=code, age_thinning=age_thinning, age_thinning_save=age_thinning_save
            )
            ReferenceData._used_breeds[name] = value_used

            for (area, breed, condition), value in list(ReferenceData._private_graphics.items()):
                if breed == old_name:
                    ReferenceData.update_name_file_graphic(
                        old_name=f"{ReferenceData.get_value_area(area)}_{old_value}_{ReferenceData.get_value_condition(condition)}",
                        new_name=f"{ReferenceData.get_value_area(area)}_{ReferenceData.get_value_breed(breed)}_{ReferenceData.get_value_condition(condition)}",
                    )
                    del ReferenceData._private_graphics[(area, old_name, condition)]
                    ReferenceData._private_graphics[(area, name, condition)] = value

        ReferenceData.save_data()

    @staticmethod
    def get_list_conditions() -> list:
        """Gets a list of all available conditions from the reference data.

        Returns:
            list: A list of strings representing all available conditions in the reference data.
                Returns keys from the _private_conditions dictionary.

        Note:
            If reference data has not been initialized, this method will automatically
            initialize it before returning the list of conditions.
        """
        if not ReferenceData._flag_initialize:
            ReferenceData.initialize_reference_data()
        return list(ReferenceData._private_conditions.keys())

    @staticmethod
    def get_list_allowed_conditions(area: str = None, breed: str = None) -> list:
        """Returns a list of unique condition values based on specified area and breed filters.

        This function filters through the private graphics data and returns a list of unique
        conditions that match the given area and breed criteria.

        Args:
            area (str, optional): The specific area to filter by. Defaults to None.
            breed (str, optional): The specific breed to filter by. Defaults to None.

        Returns:
            list: A list of unique condition values that match the specified filters.
                If no filters are provided, returns all unique conditions.
        """
        result = []
        for area_current, breed_current, condition_current in ReferenceData._private_graphics.keys():
            if (breed is None or breed == breed_current) and (area is None or area == area_current):
                if condition_current not in result:
                    result.append(condition_current)
        return result

    @staticmethod
    def get_list_conditions_used() -> list:
        """Returns a list of tuples containing condition keys and their usage status.

        This method creates a list of tuples where each tuple contains a condition key and
        a boolean value indicating whether that condition has been used.

        Returns:
            list: A list of tuples in the format [(condition_key, is_used)], where:
                - condition_key: The key identifying the condition
                - is_used: Boolean indicating whether the condition has been used
        """
        result = []
        for key in ReferenceData._private_conditions.keys():
            result.append((key, ReferenceData._used_conditions[key]))
        return result

    @staticmethod
    def check_used_condition(name: str) -> bool:
        """Checks if a condition with the given name has been used.

        Args:
            name (str): The name of the condition to check.

        Returns:
            bool: True if the condition has been used, False otherwise.
        """
        return ReferenceData._used_conditions.get(name, False)

    @staticmethod
    def get_value_condition(name: str) -> str:
        """Gets the condition associated with a given name from private conditions.

        Args:
            name (str): The name of the condition to retrieve.

        Returns:
            str: The condition value associated with the given name. Returns None if the name
                is not found in the private conditions dictionary.
        """
        return ReferenceData._private_conditions.get(name)

    @staticmethod
    def exist_name_condition(name: str) -> bool:
        """Checks if the given condition name exists in the private conditions dictionary.

        Args:
            name (str): The name of the condition to check.

        Returns:
            bool: True if the condition name exists in the private conditions, False otherwise.
        """
        return name in ReferenceData._private_conditions

    @staticmethod
    def exist_code_condition(code: str) -> bool:
        """Checks if a given condition code exists in the private conditions dictionary.

        Args:
            code (str): The condition code to check for existence.

        Returns:
            bool: True if the code exists in the conditions dictionary, False otherwise.
        """
        return code in ReferenceData._private_conditions.values()

    @staticmethod
    def add_conditions(name: str, code: str) -> None:
        """Adds a new condition with its code to the reference data.

        Adds a new condition name and its corresponding code to the private conditions dictionary
        and initializes its usage status as False. The data is saved after the addition.

        Args:
            name (str): Name of the condition to be added.
            code (str): Code associated with the condition.

        Raises:
            ValueError: If the condition name or code already exists in the reference data.
        """
        if ReferenceData.exist_name_condition(name):
            raise ValueError(f"Condition '{name}' already exists")
        if ReferenceData.exist_code_condition(code):
            raise ValueError(f"Code condition'{code}' already exists")

        with ReferenceData.transaction():
            ReferenceData._private_conditions[name] = code
            ReferenceData._used_conditions[name] = False
        ReferenceData.save_data()

    @staticmethod
    def delete_condition(name: str) -> None:
        """Deletes a condition from reference data if it's not in use.

        Args:
            name (str): The name of the condition to be deleted.

        Raises:
            ValueError: If the condition is currently in use.

        Note:
            This operation is performed within a transaction and automatically saves
            the updated data.
        """
        if ReferenceData._used_conditions[name]:
            raise ValueError("Impossible delete used condition")
        with ReferenceData.transaction():
            del ReferenceData._private_conditions[name]
            del ReferenceData._used_conditions[name]
        ReferenceData.save_data()

    @staticmethod
    def update_conditions(old_name: str, name: str, code: str) -> None:
        """Updates the condition in the reference data.

        Updates the name and code of an existing condition in the reference data storage.
        Also updates all related graphics files that use this condition.

        Args:
            old_name (str): The current name of the condition to be updated.
            name (str): The new name for the condition.
            code (str): The new code for the condition.

        Raises:
            ValueError: If any of these conditions are met:
                - The old_name doesn't exist in conditions
                - The new name already exists (when different from old_name)
                - The new code already exists (when different from the old condition's code)

        Note:
            This method performs the update within a transaction to ensure data consistency.
            After the update, all changes are automatically saved to persistent storage.
        """
        if not ReferenceData.exist_name_condition(old_name):
            raise ValueError("Not exist old name condition")
        if old_name != name and ReferenceData.exist_name_condition(name):
            raise ValueError("Exist name condition")
        if ReferenceData.exist_code_condition(code) and code != ReferenceData._private_conditions[old_name]:
            raise ValueError("Exist code condition")

        with ReferenceData.transaction():
            old_value = ReferenceData._private_conditions[old_name]
            del ReferenceData._private_conditions[old_name]

            value_used = ReferenceData._used_conditions[old_name]
            del ReferenceData._used_conditions[old_name]
            ReferenceData.add_conditions(name=name, code=code)
            ReferenceData._used_conditions[name] = value_used

            for (area, breed, condition), value in list(ReferenceData._private_graphics.items()):
                if condition == old_name:
                    ReferenceData.update_name_file_graphic(
                        old_name=f"{ReferenceData.get_value_area(area)}_{ReferenceData.get_value_breed(breed)}_{old_value}",
                        new_name=f"{ReferenceData.get_value_area(area)}_{ReferenceData.get_value_breed(breed)}_{ReferenceData.get_value_condition(condition)}",
                    )
                    del ReferenceData._private_graphics[(area, breed, old_name)]
                    ReferenceData._private_graphics[(area, breed, name)] = value

        ReferenceData.save_data()

    @staticmethod
    def get_name_graphic(area: str, breed: str, condition: str) -> str:
        """Creates a formatted string combining area, breed, and condition values.

        This function concatenates the values retrieved from ReferenceData for area, breed,
        and condition using underscores as separators.

        Args:
            area (str): The area identifier to be converted using ReferenceData.
            breed (str): The breed identifier to be converted using ReferenceData.
            condition (str): The condition identifier to be converted using ReferenceData.

        Returns:
            str: A string in the format "area_breed_condition" where each component
                is converted using respective ReferenceData methods.
        """
        return (
            f"{ReferenceData.get_value_area(name=area)}_"
            + f"{ReferenceData.get_value_breed(name=breed)}_"
            + f"{ReferenceData.get_value_condition(name=condition)}"
        )

    @staticmethod
    def get_list_graphics() -> list:
        """Gets a list of all available graphic keys.

        Returns:
            list: A list of strings representing the keys of available graphics.

        Note:
            If reference data is not initialized, this method will automatically initialize it
            before returning the list of graphics.
        """
        if not ReferenceData._flag_initialize:
            ReferenceData.initialize_reference_data()
        return list(ReferenceData._private_graphics.keys())

    @staticmethod
    def exist_graphic(name_area: str, name_breed: str, name_condition: str) -> bool:
        """Checks if a graphic exists for the given combination of area, breed, and condition.

        Args:
            name_area (str): The name of the area.
            name_breed (str): The name of the tree breed.
            name_condition (str): The condition name.

        Returns:
            bool: True if a graphic exists for the given parameters, False otherwise.
        """
        return (name_area, name_breed, name_condition) in ReferenceData._private_graphics

    @staticmethod
    def get_value_graphic(name_area: str, name_breed: str, name_condition: str) -> str | None:
        """Retrieves the graphic value for given area, breed and condition parameters.

        Args:
            name_area (str): Name of the forest area
            name_breed (str): Name of the tree breed
            name_condition (str): Condition category of the forest

        Returns:
            str: The corresponding graphic value from the private graphics dictionary.
                Returns None if no matching combination is found.
        """
        return ReferenceData._private_graphics.get((name_area, name_breed, name_condition))

    @staticmethod
    def add_graphic(name_area: str, name_breed: str, name_condition: str, path_file: Path) -> None:
        """Adds a new graphic to the reference data system.

        This method copies a graphic file to the data directory and registers it in the system
        using the specified parameters. The operation is performed within a transaction to ensure
        data consistency.

        Args:
            name_area (str): The name of the area for the graphic.
            name_breed (str): The name of the breed for the graphic.
            name_condition (str): The name of the condition for the graphic.
            path_file (Path): The path to the source graphic file to be added.

        Raises:
            ValueError: If any of the parameter values (area, breed, condition) are not found
                in their respective reference collections, or if a graphic with the same
                combination of parameters already exists.

        Returns:
            None
        Note:
            The method will create the data directory if it doesn't exist.
            The operation is atomic due to the use of a transaction.
        """
        if not (
            name_area in ReferenceData._private_areas
            and name_breed in ReferenceData._private_breeds
            and name_condition in ReferenceData._private_conditions
        ):
            raise ValueError("Invalid parameter value")

        if ReferenceData.exist_graphic(name_area=name_area, name_breed=name_breed, name_condition=name_condition):
            raise ValueError("The key is not unique")
        file_name = ReferenceData.get_name_graphic(
            area=ReferenceData._private_areas[name_area],
            breed=ReferenceData._private_breeds[name_breed]["value"],
            condition=ReferenceData._private_conditions[name_condition],
        )
        if not Paths.DATA_DIRECTORY.exists():
            Paths.DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
        target_path = Paths.DATA_DIRECTORY / file_name

        with ReferenceData.transaction():
            shutil.copy(path_file, target_path)

            ReferenceData._private_graphics[(name_area, name_breed, name_condition)] = ReferenceData.get_name_graphic(
                area=name_area, breed=name_breed, condition=name_condition
            )
            ReferenceData._used_areas[name_area] = True
            ReferenceData._used_breeds[name_breed] = True
            ReferenceData._used_conditions[name_condition] = True
        ReferenceData.save_data()

    @staticmethod
    def delete_graphic(name_area: str, name_breed: str, name_condition: str) -> None:
        """Deletes a graphic file and its reference from the data structure.

        Args:
            name_area (str): The name of the area associated with the graphic.
            name_breed (str): The name of the breed associated with the graphic.
            name_condition (str): The name of the condition associated with the graphic.

        Returns:
            None

        Raises:
            KeyError: If the specified combination of area, breed, and condition doesn't exist.
            OSError: If there's an error while deleting the file.
        """
        file_path = Paths.DATA_DIRECTORY / (
            f"{str(ReferenceData._private_graphics[(name_area, name_breed, name_condition)])}.tar"
        )
        with ReferenceData.transaction():
            os.remove(file_path)
            del ReferenceData._private_graphics[(name_area, name_breed, name_condition)]
            ReferenceData.refresh_used_element()
        ReferenceData.save_data()

    @staticmethod
    def update_name_file_graphic(old_name: str, new_name: str) -> None:
        """Renames a compressed file containing graphic data from old name to new name.

        Args:
            old_name (str): Current name of the file (without extension)
            new_name (str): New name to be assigned to the file (without extension).

        Returns:
            None: Function performs file renaming operation and doesn't return any value
        Raises:
            OSError: If the source file doesn't exist or if there's an error during renaming
            TypeError: If the input parameters are not strings.
        """  # noqa: D205
        old_path = Paths.DATA_DIRECTORY / f"{old_name}.tar"
        new_path = Paths.DATA_DIRECTORY / f"{new_name}.tar"
        os.rename(old_path, new_path)

    @staticmethod
    def refresh_used_element() -> None:
        """Updates the usage status of reference data elements.

        Resets all usage flags to False and then marks elements as True if they are
        being used in private graphics. This method helps track which areas, breeds,
        and conditions are actively in use.

        The method operates on three dictionaries tracking the usage of:
            - Areas (_used_areas)
            - Breeds (_used_breeds)
            - Conditions (_used_conditions)

        First, it resets all flags to False, then sets them to True based on the
        keys present in _private_graphics.

        Returns:
            None
        """
        for key in ReferenceData._used_areas.keys():
            ReferenceData._used_areas[key] = False
        for key in ReferenceData._used_breeds.keys():
            ReferenceData._used_breeds[key] = False
        for key in ReferenceData._used_conditions.keys():
            ReferenceData._used_conditions[key] = False

        for area, breed, condition in ReferenceData._private_graphics.keys():
            ReferenceData._used_areas[area] = True
            ReferenceData._used_breeds[breed] = True
            ReferenceData._used_conditions[condition] = True

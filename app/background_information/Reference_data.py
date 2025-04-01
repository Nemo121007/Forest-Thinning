"""Data class for reference data."""

from app.background_information.Paths import Paths
import json


class ReferenceData:
    """A class for managing reference data including areas, breeds, and type conditions.

    This class provides functionality to load, store, and manage reference data
    from a JSON file. It maintains three main types of data: areas, breeds, and
    type conditions. The data is stored in private class variables and can be
    accessed through public methods.

    Attributes:
        _private_areas (dict): Dictionary storing area data with area names as keys
            and their corresponding codes as values.
        _private_breeds (dict): Dictionary storing breed data with breed names as keys
            and their corresponding codes as values.
        _private_types_conditions (dict): Dictionary storing condition types with
            condition names as keys and their corresponding codes as values.
        _flag_initialize (bool): Flag indicating whether the reference data has
            been initialized.

    Note:
        All data is persisted to a JSON file specified by Paths.REFERENCE_DATA.
        The class uses static methods for all operations, functioning as a singleton.
    """

    _private_areas = {}
    _private_breeds = {}
    _private_types_conditions = {}
    _flag_initialize = False

    @staticmethod
    def initialize_reference_data():
        """Initialize reference data by loading it from a JSON file.

        This method checks if the reference data file exists and loads the data
        from it if present. The data includes areas, breeds, and type conditions
        which are stored in their respective private class variables.

        The method sets the initialization flag to True after successful loading.

        Note:
            The file path is determined by Paths.REFERENCE_DATA constant.
            The JSON file should contain "areas", "breeds" and "types_conditions" keys.

        Returns:
            None
        """
        if Paths.REFERENCE_DATA.exists():
            with open(Paths.REFERENCE_DATA) as file:
                reference_data = json.load(file)
                ReferenceData._private_areas = reference_data["areas"]
                ReferenceData._private_breeds = reference_data["breeds"]
                ReferenceData._private_types_conditions = reference_data["types_conditions"]
            ReferenceData._flag_initialize = True

    @staticmethod
    def areas() -> dict:
        """Retrieves the private areas data from the ReferenceData class.

        This function ensures that the reference data is initialized before
        accessing the private areas. If the data has not been initialized,
        it calls the `initialize_reference_data` method to perform the initialization.

        Args:
            None.

        Returns:
            list: The private areas data stored in `ReferenceData._private_areas`.
        """
        if not ReferenceData._flag_initialize:
            ReferenceData.initialize_reference_data()
        return ReferenceData._private_areas

    @staticmethod
    def breeds() -> dict:
        """Retrieves the list of private breeds from the reference data.

        If the reference data has not been initialized, this function will
        initialize it before returning the breeds.

        Args:
            None.

        Returns:
            list: A list of private breeds stored in the reference data.
        """
        if not ReferenceData._flag_initialize:
            ReferenceData.initialize_reference_data()
        return ReferenceData._private_breeds

    @staticmethod
    def type_conditions() -> dict:
        """Retrieve the private type conditions from the ReferenceData class.

        This function ensures that the reference data is initialized before
        accessing the private type conditions. If the reference data has not
        been initialized, it calls the `initialize_reference_data` method
        of the ReferenceData class.

        Args:
            None.

        Returns:
            dict: The private type conditions stored in the ReferenceData class.
        """
        if not ReferenceData._flag_initialize:
            ReferenceData.initialize_reference_data()
        return ReferenceData._private_types_conditions

    @staticmethod
    def add_areas(code_name: str, name_areas: str) -> None:
        """Adds a new area to the private areas dictionary with the specified code name and area name.

        Args:
            code_name (str): The code name associated with the area.
            name_areas (str): The name of the area to be added.

        Returns:
            None
        """
        ReferenceData._private_areas[name_areas] = code_name

    @staticmethod
    def add_breeds(code_name: str, name_breed: str) -> None:
        """Adds a new breed to the private breeds dictionary.

        Args:
            code_name (str): The code name associated with the breed.
            name_breed (str): The name of the breed to be added.

        Returns:
            None
        """
        ReferenceData._private_breeds[name_breed] = code_name

    @staticmethod
    def add_type_conditions(code_name: str, name_type_conditions: str) -> None:
        """Adds a new type condition to the private types conditions dictionary.

        Args:
            code_name (str): The code name associated with the type condition.
            name_type_conditions (str): The name of the type condition to be added.

        Returns:
            None.
        """
        ReferenceData._private_types_conditions[name_type_conditions] = code_name

    @staticmethod
    def save_data():
        """Saves reference data to a JSON file.

        This function collects reference data from the `ReferenceData` class,
        including areas, breeds, and types of conditions, and writes it to a
        JSON file specified by `Paths.REFERENCE_DATA`. The data is saved with
        UTF-8 encoding, formatted with an indentation of 4 spaces, and ensures
        non-ASCII characters are preserved.

        Args:
            None.

        Raises:
            OSError: If there is an issue writing to the file, an OSError is raised
            with a descriptive error message.
        """
        try:
            reference_data = {
                "areas": ReferenceData._private_areas,
                "breeds": ReferenceData._private_breeds,
                "types_conditions": ReferenceData._private_types_conditions,
            }

            with open(Paths.REFERENCE_DATA, "w", encoding="utf-8") as file:
                json.dump(reference_data, file, indent=4, ensure_ascii=False)
        except OSError as e:
            raise OSError(f"Error save file: {e}")

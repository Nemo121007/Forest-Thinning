"""Module for managing graphics-related data in a reference data system.

This module provides the GraphicsService class, which interacts with a ReferenceDataManager
and PredictModelService to perform operations on graphics data, including retrieval,
addition, deletion, and validation of graphics associated with areas, breeds, and conditions.
"""

from .ReferenceDataManagerService import ReferenceDataManagerServices
from .PredictModelServices import PredictModelService


class GraphicsService:
    """A service class for managing graphics data.

    Provides methods to interact with graphics data through a ReferenceDataManager instance,
    including retrieving graphic names, checking existence, and performing CRUD operations.
    Integrates with PredictModelService for model initialization and deletion. Saves changes
    to persistent storage via the manager.

    Attributes:
        manager (ReferenceDataManager): The reference data manager instance.
        graphics (object): The graphics data entity managed by ReferenceDataManager.
        predict_model (PredictModelService): Service for managing prediction models.
    """

    def __init__(self):
        """Initialize the GraphicsService.

        Sets up the service by retrieving the ReferenceDataManager instance, accessing its
        graphics entity, and initializing the PredictModelService.

        Returns:
            None
        """
        self.manager = ReferenceDataManagerServices().manager
        self.graphics = self.manager.get_graphics()
        self.predict_model = PredictModelService()

    def get_name_graphic(self, area: str, breed: str, condition: str) -> str:
        """Retrieve the name of a graphic based on area, breed, and condition.

        Args:
            area (str): The name of the area.
            breed (str): The name of the breed.
            condition (str): The name of the condition.

        Returns:
            str: The name of the graphic.

        Raises:
            Exception: If an error occurs while retrieving the graphic name.
        """
        try:
            result = self.graphics.get_name_graphic(area=area, breed=breed, condition=condition)
            return result
        except Exception as e:
            raise Exception(f"Error get name condition {str(e)}")

    def get_list_graphics(self) -> list[str]:
        """Retrieve a list of all graphics.

        Returns:
            list[str]: A list of graphics, typically as tuples of (area, breed, condition).

        Raises:
            Exception: If an error occurs while retrieving the list of graphics.
        """
        try:
            result = self.graphics.get_list_graphics()
            return result
        except Exception as e:
            raise Exception(f"Error get list graphic {str(e)}")

    def exist_graphic(self, name_area: str, name_breed: str, name_condition: str) -> bool:
        """Check if a graphic exists for the given area, breed, and condition.

        Args:
            name_area (str): The name of the area.
            name_breed (str): The name of the breed.
            name_condition (str): The name of the condition.

        Returns:
            bool: True if the graphic exists, False otherwise.

        Raises:
            Exception: If an error occurs while checking the graphic's existence.
        """
        try:
            result = self.graphics.exist_graphic(
                name_area=name_area, name_breed=name_breed, name_condition=name_condition
            )
            return result
        except Exception as e:
            raise Exception(f"Error exist graphic {str(e)}")

    def get_value_graphic(self, name_area: str, name_breed: str, name_condition: str) -> bool:
        """Retrieve the value (e.g., file path) associated with a graphic.

        Args:
            name_area (str): The name of the area.
            name_breed (str): The name of the breed.
            name_condition (str): The name of the condition.

        Returns:
            str: The value associated with the graphic (e.g., file path).

        Raises:
            Exception: If an error occurs while retrieving the graphic value.
        """
        try:
            result = self.graphics.get_value_graphic(
                name_area=name_area, name_breed=name_breed, name_condition=name_condition
            )
            return result
        except Exception as e:
            raise Exception(f"Error get value graphic {str(e)}")

    def add_graphic(self, name_area: str, name_breed: str, name_condition: str, path_file: str) -> None:
        """Add a new graphic.

        Adds a graphic associated with the specified area, breed, condition, and file path,
        then saves the changes to persistent storage.

        Args:
            name_area (str): The name of the area.
            name_breed (str): The name of the breed.
            name_condition (str): The name of the condition.
            path_file (str): The file path associated with the graphic.

        Returns:
            None

        Raises:
            Exception: If an error occurs while adding the graphic.
        """
        try:
            self.graphics.add_graphic(
                name_area=name_area, name_breed=name_breed, name_condition=name_condition, path_file=path_file
            )
            self.predict_model.initialize_predict_model(
                area=name_area, breed=name_breed, condition=name_condition, flag_prepare_model=True
            )
            self.predict_model.save_model()
            self.manager.save_data()
        except Exception as e:
            raise Exception(f"Error add file {str(e)}")

    def delete_graphic(self, name_area: str, name_breed: str, name_condition: str) -> None:
        """Delete an existing graphic.

        Removes the graphic associated with the specified area, breed, and condition,
        then saves the changes to persistent storage.

        Args:
            name_area (str): The name of the area.
            name_breed (str): The name of the breed.
            name_condition (str): The name of the condition.

        Returns:
            None

        Raises:
            Exception: If an error occurs while deleting the graphic.
        """
        try:
            self.graphics.delete_graphic(name_area=name_area, name_breed=name_breed, name_condition=name_condition)
            self.manager.save_data()
            self.predict_model.delete_model(area=name_area, breed=name_breed, condition=name_condition)
        except Exception as e:
            raise Exception(f"Error delete graphic {str(e)}")

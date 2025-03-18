"""Data class for reference data."""

from app.background_information.Paths import Paths
import json


class ReferenceData:
    """ReferenceData class.

    This class is used to store the reference data for type forest, breed, and area.
    """

    def __init__(self):
        """Initiate the ReferenceData class.

        This class is used to store the reference data for type forest, breed, and area.

        Args:
            None

        Returns:
            None
        """
        self.areas = {}
        self.breeds = {}
        self.types_conditions = {}

        if Paths.REFERENCE_DATA.exists():
            with open(Paths.REFERENCE_DATA) as file:
                reference_data = json.load(file)
                self.areas = reference_data["areas"]
                self.breeds = reference_data["breeds"]
                self.types_conditions = reference_data["types_conditions"]

        pass

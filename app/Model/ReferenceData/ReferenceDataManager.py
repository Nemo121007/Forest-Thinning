"""Module for managing reference data in a centralized system.

This module provides the ReferenceDataManager class, which coordinates the initialization,
persistence, and retrieval of reference data entities (Areas, Breeds, Conditions, Graphics).
It handles loading and saving data to a JSON file and ensures consistency across entities.
"""

import json
from app.background_information.Paths import Paths
from app.Model.ReferenceData.Areas import Areas
from app.Model.ReferenceData.Breeds import Breeds
from app.Model.ReferenceData.Conditions import Conditions
from app.Model.ReferenceData.Graphics import Graphics


class ReferenceDataManager:
    """A class for managing reference data entities.

    Coordinates the initialization, persistence, and retrieval of Areas, Breeds, Conditions,
    and Graphics entities. Loads data from a JSON file on initialization, saves changes to
    the same file, and ensures dependencies between entities are properly set up.

    Attributes:
        _cached_data (dict, optional): Cached data loaded from the JSON file.
        _areas (Areas): The Areas entity for managing area data.
        _breeds (Breeds): The Breeds entity for managing breed data.
        _conditions (Conditions): The Conditions entity for managing condition data.
        _graphics (Graphics): The Graphics entity for managing graphic data.
        _initialized (bool): Flag indicating whether the manager has been initialized.
    """

    def __init__(self):
        """Initialize the ReferenceDataManager.

        Sets up the Areas, Breeds, Conditions, and Graphics entities, establishes their
        dependencies, and triggers initial data loading.
        """
        self._cached_data = None  # Кэш из внешнего файла
        self._areas = Areas()
        self._breeds = Breeds()
        self._conditions = Conditions()
        self._graphics = Graphics(self._areas, self._breeds, self._conditions)
        self._initialized = False
        # Установить Graphics после создания(избежание циклической зависимости)
        self._areas._graphics = self._graphics
        self._breeds._graphics = self._graphics
        self._conditions._graphics = self._graphics
        self.initialize()

    def initialize(self):
        """Load and initialize reference data entities.

        Loads data from the JSON file specified in Paths.REFERENCE_DATA if available,
        otherwise uses an empty dataset. Initializes all entities (Areas, Breeds, Conditions,
        Graphics) with the loaded data and refreshes usage tracking for graphics.

        Returns:
            None

        Raises:
            Exception: If an error occurs while loading or parsing the JSON file.
        """
        if self._cached_data is None:
            if Paths.REFERENCE_DATA.exists():
                with open(Paths.REFERENCE_DATA, encoding="utf-8") as file:
                    try:
                        data = dict(json.load(file))
                        self._cached_data = data
                    except Exception:
                        data = {}
            else:
                data = {}
        else:
            data = self._cached_data

        self._areas.initialize(data)
        self._breeds.initialize(data)
        self._conditions.initialize(data)
        self._graphics.initialize(data)
        self._initialized = True
        self._graphics.refresh_used_elements()

    def save_data(self) -> None:
        """Save reference data to the JSON file.

        Collects data from all entities (Areas, Breeds, Conditions, Graphics), saves it to
        the JSON file specified in Paths.REFERENCE_DATA, and ensures the parent directory
        exists.

        Returns:
            None
        """
        reference_data = {}
        self._areas.save_data(reference_data)
        self._breeds.save_data(reference_data)
        self._conditions.save_data(reference_data)
        self._graphics.save_data(reference_data)

        Paths.REFERENCE_DATA.parent.mkdir(parents=True, exist_ok=True)
        with open(Paths.REFERENCE_DATA, "w", encoding="utf-8") as file:
            json.dump(reference_data, file, indent=4, ensure_ascii=False)

    def get_areas(self) -> Areas:
        """Retrieve the Areas entity.

        Ensures the manager is initialized before returning the Areas entity.

        Returns:
            Areas: The Areas entity for managing area data.
        """
        if not self._initialized:
            self.initialize()
        return self._areas

    def get_breeds(self) -> Breeds:
        """Retrieve the Breeds entity.

        Ensures the manager is initialized before returning the Breeds entity.

        Returns:
            Breeds: The Breeds entity for managing breed data.
        """
        if not self._initialized:
            self.initialize()
        return self._breeds

    def get_conditions(self) -> Conditions:
        """Retrieve the Conditions entity.

        Ensures the manager is initialized before returning the Conditions entity.

        Returns:
            Conditions: The Conditions entity for managing condition data.
        """
        if not self._initialized:
            self.initialize()
        return self._conditions

    def get_graphics(self) -> Graphics:
        """Retrieve the Graphics entity.

        Ensures the manager is initialized before returning the Graphics entity.

        Returns:
            Graphics: The Graphics entity for managing graphic data.
        """
        if not self._initialized:
            self.initialize()
        return self._graphics

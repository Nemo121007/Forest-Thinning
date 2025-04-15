"""Module for defining file system paths in a reference data system.

This module provides the Paths class, a dataclass that defines key file system paths
used throughout the application, such as directories for data, models, and reference data.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Paths:
    """A dataclass for defining file system paths used in the application.

    Stores paths for the root directory, data storage, model storage, and reference data
    as Path objects, providing a centralized configuration for file system access.

    Attributes:
        ROOT (Path): The root directory of the project, derived from the location of this file.
        DATA_DIRECTORY (Path): Directory for storing data files, located at ROOT/data/data_line.
        MODEL_DIRECTORY (Path): Directory for storing model-related files, located at ROOT/data/model_saving.
        REFERENCE_DATA (Path): Path to the reference data JSON file, located at ROOT/data/reference_data.json.
    """

    ROOT: Path = Path(__file__).parent.parent.parent

    DATA_DIRECTORY: Path = ROOT / "data" / "data_line"

    MODEL_DIRECTORY: Path = ROOT / "data" / "model_saving"

    REFERENCE_DATA: Path = ROOT / "data" / "reference_data.json"

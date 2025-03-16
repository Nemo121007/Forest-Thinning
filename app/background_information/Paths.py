"""Dataclass."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Paths:
    """Dataclass."""

    ROOT: Path = Path(__file__).parent.parent.parent

    DATA_DIRECTORY: Path = ROOT / "data" / "data_line"

    MODEL_DIRECTORY: Path = ROOT / "data" / "model_saving"
    MODEL_DIRECTORY_INFO: Path = MODEL_DIRECTORY / "data" / "saving_model.json"
    MODEL_DIRECTORY_MODELS: Path = MODEL_DIRECTORY / "data" / "models"

    REFERENCE_DATA: Path = ROOT / "data" / "reference_data.json"

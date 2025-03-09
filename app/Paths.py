"""Dataclass."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Paths:
    """Dataclass."""

    ROOT: Path = Path(__file__).parent.parent

    DATA_DIRECTORY: Path = ROOT / "data_line"

    MODEL_DIRECTORY: Path = ROOT / "model_saving"
    MODEL_DIRECTORY_INFO: Path = MODEL_DIRECTORY / "saving_model.json"
    MODEL_DIRECTORY_MODELS: Path = MODEL_DIRECTORY / "models"

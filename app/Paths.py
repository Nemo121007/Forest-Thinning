"""Dataclass."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Paths:
    """Dataclass."""

    ROOT: Path = Path(__file__).parent
    DATA_DIRECTORY: Path = ROOT / "data_line"

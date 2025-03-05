from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Paths:
    root: Path = Path(__file__).parent  
    DATA_DIRECTORY: Path = field(init=False)

    def __post_init__(self):
        self.DATA_DIRECTORY = self.root / "data_line"
        
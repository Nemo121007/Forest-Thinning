"""Module for storing graph metadata in forest growth and thinning simulations.

This module defines the GraphData dataclass, which encapsulates metadata for a graph,
including area, breed, condition, thinning ages, and min/max values for plotting.
It provides methods to update reference codes and retrieve plotting boundaries.

Dependencies:
    - dataclasses: Standard library module for defining the GraphData dataclass.
"""

from dataclasses import dataclass


@dataclass
class GraphData:
    """Dataclass for storing metadata of a graph in forest growth simulations.

    Encapsulates essential attributes for a graph, such as its name, associated area,
    breed, condition, thinning ages, and plotting boundaries. Provides methods to update
    reference codes and retrieve min/max values for plotting.

    Attributes:
        name (str): The name of the graph (e.g., file name).
        area (str): The name of the area associated with the graph.
        breed (str): The name of the breed associated with the graph.
        condition (str): The name of the condition associated with the graph.
        age_thinning (float): The age of thinning for the breed.
        age_thinning_save (float): The age of thinning for protective forests.
        code_area (str | None): The code for the area, defaults to None.
        code_breed (str | None): The code for the breed, defaults to None.
        code_condition (str | None): The code for the condition, defaults to None.
        flag_save_forest (bool): Flag indicating protective forest mode, defaults to False.
        x_max (float | None): Maximum x-value for plotting, defaults to None.
        x_min (float | None): Minimum x-value for plotting, defaults to None.
        y_max (float | None): Maximum y-value for plotting, defaults to None.
        y_min (float | None): Minimum y-value for plotting, defaults to None.
        x_min_economic (float | None): Minimum x-value for economic considerations, defaults to None.
    """

    name: str
    area: str
    breed: str
    condition: str
    age_thinning: float
    age_thinning_save: float

    code_area: str | None = None
    code_breed: str | None = None
    code_condition: str | None = None
    flag_save_forest: bool = False
    x_max: float | None = None
    x_min: float | None = None
    y_max: float | None = None
    y_min: float | None = None
    x_min_economic: float | None = None

    def update_codes(
        self, code_area: str | None = None, code_breed: str | None = None, code_condition: str | None = None
    ) -> None:
        """Update reference codes for area, breed, and condition.

        Updates code_area, code_breed, and code_condition attributes if the provided values
        are non-empty strings. Ignores None values, preserving existing codes.

        Args:
            code_area (str | None, optional): The new area code. Defaults to None.
            code_breed (str | None, optional): The new breed code. Defaults to None.
            code_condition (str | None, optional): The new condition code. Defaults to None.

        Returns:
            None

        Raises:
            ValueError: If any provided code is not a non-empty string.
        """
        codes = {
            "code_area": code_area,
            "code_breed": code_breed,
            "code_condition": code_condition,
        }
        for attr, value in codes.items():
            if value is not None:
                if not isinstance(value, str) or not value:
                    raise ValueError(f"Code {attr} must be a non-empty string")
                setattr(self, attr, value)

    def get_min_max_value(self) -> tuple[float, float, float, float]:
        """Retrieve the minimum and maximum x and y values for plotting.

        Returns a tuple of x_min, x_max, y_min, and y_max values, ensuring all are defined
        and valid (x_min <= x_max, y_min <= y_max).

        Returns:
            tuple[float, float, float, float]: A tuple containing (x_min, x_max, y_min, y_max).

        Raises:
            ValueError: If any of x_min, x_max, y_min, or y_max is None, or if x_min > x_max
                or y_min > y_max.
        """
        if any(v is None for v in [self.x_min, self.x_max, self.y_min, self.y_max]):
            raise ValueError("Graph metadata (x_min, x_max, y_min, y_max) is not fully initialized")
        if self.x_min > self.x_max or self.y_min > self.y_max:
            raise ValueError("Invalid min/max values: x_min must be <= x_max, y_min must be <= y_max")
        return self.x_min, self.x_max, self.y_min, self.y_max

    def to_dict(self) -> dict:
        """Convert the GraphData instance to a dictionary.

        Returns a dictionary containing all attributes of the GraphData instance, suitable
        for serialization.

        Returns:
            dict: A dictionary with keys corresponding to attribute names and their values.
        """
        return {
            "name": self.name,
            "area": self.area,
            "code_area": self.code_area,
            "breed": self.breed,
            "code_breed": self.code_breed,
            "condition": self.condition,
            "code_condition": self.code_condition,
            "age_thinning": self.age_thinning,
            "age_thinning_save": self.age_thinning_save,
            "x_max": self.x_max,
            "x_min": self.x_min,
            "y_max": self.y_max,
            "y_min": self.y_min,
            "x_min_economic": self.x_min_economic,
            "flag_save_forest": self.flag_save_forest,
        }

    def from_dict(self, data: dict) -> None:
        """Update the GraphData instance from a dictionary.

        Populates the instance's attributes from the provided dictionary, converting values
        to appropriate types where necessary. Missing optional fields are set to their default
        values.

        Args:
            data (dict): A dictionary containing attribute names and values. Required keys:
                'name', 'area', 'breed', 'condition', 'age_thinning', 'age_thinning_save'.
                Optional keys: 'code_area', 'code_breed', 'code_condition', 'flag_save_forest',
                'x_max', 'x_min', 'y_max', 'y_min', 'x_min_economic'.

        Returns:
            None

        Raises:
            KeyError: If any required key is missing from the dictionary.
            TypeError: If required fields have incorrect types (e.g., non-string name).
        """
        self.name = str(data["name"])
        self.area = str(data["area"])
        self.breed = str(data["breed"])
        self.condition = str(data["condition"])
        self.age_thinning = data["age_thinning"]
        self.age_thinning_save = data["age_thinning_save"]
        self.code_area = data.get("code_area")
        self.code_breed = data.get("code_breed")
        self.code_condition = data.get("code_condition")
        self.flag_save_forest = data.get("flag_save_forest", False)
        self.x_max = data.get("x_max")
        self.x_min = data.get("x_min")
        self.y_max = data.get("y_max")
        self.y_min = data.get("y_min")
        self.x_min_economic = data.get("x_min_economic")

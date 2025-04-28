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

        Updates the code_area, code_breed, and code_condition attributes if the corresponding
        arguments are provided (not None). Ignores None values, preserving existing codes.

        Args:
            code_area (str | None, optional): The new area code. Defaults to None.
            code_breed (str | None, optional): The new breed code. Defaults to None.
            code_condition (str | None, optional): The new condition code. Defaults to None.

        Returns:
            None
        """
        if code_area is not None:
            self.code_area = code_area
        if code_breed is not None:
            self.code_breed = code_breed
        if code_condition is not None:
            self.code_condition = code_condition

    def get_min_max_value(self) -> tuple[float, float, float, float]:
        """Retrieve the minimum and maximum x and y values for plotting.

        Returns a tuple of x_min, x_max, y_min, and y_max values, ensuring all are defined.

        Returns:
            tuple[float, float, float, float]: A tuple containing (x_min, x_max, y_min, y_max).

        Raises:
            ValueError: If any of x_min, x_max, y_min, or y_max is None.
        """
        if any(v is None for v in [self.x_min, self.x_max, self.y_min, self.y_max]):
            raise ValueError("Graph metadata is not fully initialized")
        return self.x_min, self.x_max, self.y_min, self.y_max

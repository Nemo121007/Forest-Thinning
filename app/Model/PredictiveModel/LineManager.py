"""Module for managing Line objects associated with TypeLine enums.

This module defines the LineManager class, which handles a collection of Line objects
mapped to TypeLine enums (e.g., growth, logging, recovery lines). It provides functionality
for adding, retrieving, training, and predicting with Line objects, used in the context
of forest growth and thinning simulations.

Dependencies:
    - Line: Class representing a single line model with regression capabilities.
    - TypeLine: Enum defining types of lines (e.g., GROWTH_LINE, RECOVERY_LINE).
"""

from .Line import Line
from ...background_information.TypeLine import TypeLine


class LineManager:
    """Manager for handling multiple Line objects associated with TypeLine enums.

    Stores a collection of Line objects in a dictionary, where keys are TypeLine enums
    (e.g., growth, logging, recovery lines). Provides methods to add, retrieve, train, and
    clear training data for Line objects, as well as predict values for specific x-coordinates
    or ranges.

    Attributes:
        lines (dict[TypeLine, Line]): A dictionary mapping TypeLine enums to Line objects.
    """

    def __init__(self):
        """Initialize an empty LineManager.

        Creates an empty dictionary to store Line objects associated with TypeLine enums.

        Returns:
            None
        """
        self.lines: dict[TypeLine, Line] = {}

    def add_line(self, type_line: TypeLine, line: Line) -> None:
        """Add a Line object to the manager.

        Associates the provided Line object with the specified TypeLine enum in the lines
        dictionary.

        Args:
            type_line (TypeLine): The type of line (e.g., growth, logging, recovery).
            line (Line): The Line object to add.

        Returns:
            None
        """
        self.lines[type_line] = line

    def get_line(self, type_line: TypeLine) -> Line:
        """Retrieve a Line object by its TypeLine.

        Returns the Line object associated with the specified TypeLine enum.

        Args:
            type_line (TypeLine): The type of line to retrieve.

        Returns:
            Line: The Line object associated with the specified TypeLine.

        Raises:
            ValueError: If the specified Type tygodniuLine is not found in the lines dictionary.
        """
        if type_line not in self.lines:
            raise ValueError(f"Type line {type_line} not found")
        return self.lines[type_line]

    def fit_models(self) -> None:
        """Fit regression models for all Line objects.

        Iterates through all Line objects in the lines dictionary and calls their
        fit_regression method to train their regression models. Prints errors if fitting
        fails for any line.

        Returns:
            None
        """
        for type_line, line in self.lines.items():
            try:
                line.fit_regression()
            except ValueError as e:
                print(f"Error fitting regression for {type_line}: {e}")

    def clear_train_data(self) -> None:
        """Clear training data for all Line objects.

        Iterates through all Line objects in the lines dictionary and calls their
        clear_train_data method to free memory used by training data. Prints errors if
        clearing fails for any line.

        Returns:
            None
        """
        for type_line, line in self.lines.items():
            try:
                line.clear_train_data()
            except ValueError as e:
                print(f"Error clearing train data for {type_line}: {e}")

    def predict_value(self, type_line: TypeLine, x: float, start_parameter: float = 0) -> float:
        """Predict a single y-value for a given x-coordinate and TypeLine.

        Retrieves the Line object for the specified TypeLine and predicts the y-value at
        the given x-coordinate, using the start_parameter for growth or recovery lines.

        Args:
            type_line (TypeLine): The type of line to predict (e.g., growth, logging).
            x (float): The x-coordinate for the prediction.
            start_parameter (float, optional): Starting parameter for the prediction, must
                be 0 for non-growth/recovery lines. Defaults to 0.

        Returns:
            float: The predicted y-value.

        Raises:
            ValueError: If the TypeLine is not found or if start_parameter is non-zero for
                non-growth/recovery lines.
        """
        line = self.get_line(type_line)
        if type_line not in (TypeLine.GROWTH_LINE, TypeLine.RECOVERY_LINE) and start_parameter != 0:
            raise ValueError(f"Invalid start_parameter {start_parameter} for {type_line}")
        return line.predict_value(x=x, start_point=start_parameter)

    def predict_list_value(self, type_line: TypeLine, x_values: list[float], start_parameter: float = 0) -> list[float]:
        """Predict y-values for a list of x-coordinates and a TypeLine.

        Retrieves the Line object for the specified TypeLine and predicts y-values for the
        provided list of x-coordinates, using the start_parameter for growth or recovery lines.

        Args:
            type_line (TypeLine): The type of line to predict (e.g., growth, logging).
            x_values (list[float]): The list of x-coordinates for predictions.
            start_parameter (float, optional): Starting parameter for the prediction, must
                be 0 for non-growth/recovery lines. Defaults to 0.

        Returns:
            list[float]: A list of predicted y-values.

        Raises:
            ValueError: If the TypeLine is not found or if start_parameter is non-zero for
                non-growth/recovery lines.
        """
        line = self.get_line(type_line)
        if type_line not in (TypeLine.GROWTH_LINE, TypeLine.RECOVERY_LINE) and start_parameter != 0:
            raise ValueError(f"Invalid start_parameter {start_parameter} for {type_line}")
        return line.predict_list_value(list_x=x_values, start_point=start_parameter)

    def predict_line(
        self, type_line: TypeLine, start_x: float, end_x: float, step: float, start_parameter: float = 0
    ) -> tuple[list[float], list[float]]:
        """Generate x and y values for a TypeLine over a range of x-coordinates.

        Retrieves the Line object for the specified TypeLine and generates x and y values
        for the range from start_x to end_x with the given step size, using the start_parameter
        for growth or recovery lines.

        Args:
            type_line (TypeLine): The type of line to predict (e.g., growth, logging).
            start_x (float): The starting x-coordinate for the range.
            end_x (float): The ending x-coordinate for the range.
            step (float): The step size between x-coordinates.
            start_parameter (float, optional): Starting parameter for the prediction, must
                be 0 for non-growth/recovery lines. Defaults to 0.

        Returns:
            tuple[list[float], list[float]]: A tuple of (x_values, y_values) for the predicted line.

        Raises:
            ValueError: If the TypeLine is not found, if start_parameter is non-zero for
                non-growth/recovery lines, or if start_x is greater than or equal to end_x.
        """
        if start_x >= end_x:
            raise ValueError(f"Invalid range: start_x ({start_x}) >= end_x ({end_x})")
        line = self.get_line(type_line)
        if type_line not in (TypeLine.GROWTH_LINE, TypeLine.RECOVERY_LINE) and start_parameter != 0:
            raise ValueError(f"Invalid start_parameter {start_parameter} for {type_line}")
        return line.predict_line(start_x=start_x, end_x=end_x, step=step, start_point=start_parameter)

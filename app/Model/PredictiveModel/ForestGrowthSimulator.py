"""Module for simulating forest growth and thinning in forest growth simulations.

This module defines the ForestGrowthSimulator class, which manages the simulation of forest
growth and thinning events. It handles base lines (minimum/maximum logging, economic minimum),
growth lines, thinning tracks, and planned thinning events using GraphData for metadata and
LineManager for line predictions.

Dependencies:
    - numpy: Library for numerical operations and array handling.
    - TypeLine: Enum defining types of lines (e.g., GROWTH_LINE, RECOVERY_LINE).
    - Settings: Class containing configuration constants (e.g., STEP_PLOTTING_GRAPH).
    - General_functions: Module with utility functions (fix_monotony, cast_coordinates_point).
    - GraphData: Dataclass for storing graph metadata.
    - LineManager: Class for managing Line objects.
"""

import numpy as np
from ...background_information.TypeLine import TypeLine
from ...background_information.Settings import Settings
from ...background_information.General_functions import fix_monotony, cast_coordinates_point
from .GraphData import GraphData
from .LineManager import LineManager


class ForestGrowthSimulator:
    """Simulator for forest growth and thinning in forest growth simulations.

    Manages the simulation of forest growth and thinning events, including base lines
    (minimum/maximum logging, economic minimum), growth lines, thinning tracks, and planned
    thinning events. Uses GraphData for metadata and LineManager for line predictions.

    Attributes:
        graph_data (GraphData): The metadata of the graph, including area, breed, and min/max values.
        line_manager (LineManager): The manager for Line objects associated with TypeLine enums.
        step (float): The step size for generating x-values, defaults to Settings.STEP_PLOTTING_GRAPH.
        x_values (np.ndarray): Array of x-coordinates for the graph.
        min_logging_y_values (np.ndarray): Y-values for the minimum logging line.
        max_logging_y_values (np.ndarray): Y-values for the maximum logging line.
        economic_min_y_values (np.ndarray): Y-values for the economic minimum line.
        growth_line_y_values (np.ndarray): Y-values for the growth line.
        growth_line_start_value (float | None): Starting parameter for the growth line, defaults to None.
        thinning_track (dict[str, list[float]]): Dictionary with x and y values for the thinning track.
        planned_thinnings (list[dict[str, float]]): List of planned thinning events, each with 'x',
            'past_value', and 'new_value' keys.
    """

    def __init__(self, graph_data: GraphData, line_manager: LineManager):
        """Initialize the ForestGrowthSimulator with graph metadata and line manager.

        Sets up the simulator with the provided GraphData and LineManager instances, initializing
        attributes for managing base lines, growth lines, and thinning simulations.

        Args:
            graph_data (GraphData): The metadata of the graph to simulate.
            line_manager (LineManager): The manager for Line objects to predict values.

        Returns:
            None
        """
        self.graph_data = graph_data
        self.line_manager = line_manager
        self.step: float = Settings.STEP_PLOTTING_GRAPH
        self.x_values: np.ndarray = np.array([], dtype=float)
        self.min_logging_y_values: np.ndarray = np.array([], dtype=float)
        self.max_logging_y_values: np.ndarray = np.array([], dtype=float)
        self.economic_min_y_values: np.ndarray = np.array([], dtype=float)
        self.growth_line_y_values: np.ndarray = np.array([], dtype=float)
        self.growth_line_start_value: float | None = None
        self.thinning_track: dict[str, list[float]] = {}
        self.planned_thinnings: list[dict[str, float]] = []

    def _generate_x_values(self, x_start: float, x_end: float, step: float) -> np.ndarray:
        """Generate an array of x-values for the simulation.

        Creates a numpy array of x-coordinates from x_start to x_end with the specified step size,
        applying coordinate casting for consistency.

        Args:
            x_start (float): The starting x-coordinate.
            x_end (float): The ending x-coordinate.
            step (float): The step size between x-values.

        Returns:
            np.ndarray: An array of x-coordinates.
        """
        x_start, _ = cast_coordinates_point(x=x_start, y=0)
        x_end, _ = cast_coordinates_point(x=x_end, y=0)
        return np.arange(x_start, x_end + step, step)

    def _predict_and_fix_y_values(
        self, type_line: TypeLine, x_values: np.ndarray, start_parameter: float
    ) -> np.ndarray:
        """Predict y-values for a line and ensure monotonicity.

        Uses LineManager to predict y-values for the specified TypeLine and x-values, then applies
        monotony correction to ensure valid predictions.

        Args:
            type_line (TypeLine): The type of line to predict (e.g., MIN_LEVEL_LOGGING).
            x_values (np.ndarray): The x-coordinates for prediction.
            start_parameter (float): The starting parameter for the prediction.

        Returns:
            np.ndarray: An array of corrected y-values.
        """
        y_values = self.line_manager.predict_list_value(
            type_line=type_line, x_values=x_values, start_parameter=start_parameter
        )
        if not isinstance(y_values, np.ndarray):
            y_values = np.array(y_values, dtype=float)
        return fix_monotony(array=y_values)

    def initialize_base_line_graph(
        self, x_start: float | None = None, x_end: float | None = None, step: float | None = None
    ) -> None:
        """Initialize base lines for the graph (minimum/maximum logging, economic minimum).

        Generates x-values and predicts y-values for minimum logging, maximum logging, and economic
        minimum lines, adjusting economic minimum values below x_min_economic to match maximum logging.

        Args:
            x_start (float, optional): Starting x-value for the range. Defaults to None (uses GraphData.x_min).
            x_end (float, optional): Ending x-value for the range. Defaults to None (uses GraphData.x_max).
            step (float, optional): Step size for x-values. Defaults to None (uses self.step).

        Returns:
            None

        Raises:
            ValueError: If graph_data.x_min, x_max, or required line models are not initialized.
        """
        if self.graph_data.x_max is None or self.graph_data.x_min is None:
            raise ValueError("Graph is not loaded or not initialized")
        required_lines = [TypeLine.MIN_LEVEL_LOGGING, TypeLine.MAX_LEVEL_LOGGING, TypeLine.ECONOMIC_MIN_LINE]
        if not all(line in self.line_manager.lines for line in required_lines):
            raise ValueError("Required line models are missing")

        x_start = x_start or self.graph_data.x_min
        x_end = x_end or self.graph_data.x_max
        step = step or self.step
        self.x_values = self._generate_x_values(x_start, x_end, step)

        self.min_logging_y_values = self._predict_and_fix_y_values(TypeLine.MIN_LEVEL_LOGGING, self.x_values, 0)
        self.max_logging_y_values = self._predict_and_fix_y_values(TypeLine.MAX_LEVEL_LOGGING, self.x_values, 0)
        self.economic_min_y_values = self._predict_and_fix_y_values(TypeLine.ECONOMIC_MIN_LINE, self.x_values, 0)

        x_min_economic, _ = cast_coordinates_point(x=self.graph_data.x_min_economic, y=0)
        mask = self.x_values < x_min_economic
        self.economic_min_y_values[mask] = self.max_logging_y_values[mask]

    def get_base_lines_graph(self) -> dict[str, list[float]]:
        """Retrieve base line data for the graph.

        Returns a dictionary containing x-values and y-values for minimum logging, maximum
        logging, and economic minimum lines, converted to lists for serialization.

        Returns:
            dict[str, list[float]]: A dictionary with keys:
                - 'list_value_x': List of x-coordinates.
                - 'list_value_y_min_logging': Y-values for minimum logging line.
                - 'list_value_y_max_logging': Y-values for maximum logging line.
                - 'list_value_y_min_economic': Y-values for economic minimum line.

        Raises:
            ValueError: If any of the base lines are not initialized.
        """
        if not all(
            [
                self.x_values.size,
                self.min_logging_y_values.size,
                self.max_logging_y_values.size,
                self.economic_min_y_values.size,
            ]
        ):
            raise ValueError("Base lines are not initialized")
        return {
            "list_value_x": self.x_values.tolist(),
            "list_value_y_min_logging": self.min_logging_y_values.tolist(),
            "list_value_y_max_logging": self.max_logging_y_values.tolist(),
            "list_value_y_min_economic": self.economic_min_y_values.tolist(),
        }

    def set_growth_line_start_value(
        self, bearing_point: tuple[float, float] | None = None, bearing_parameter: float | None = None
    ) -> None:
        """Set the starting value for the growth line.

        Sets the growth_line_start_value based on a bearing point (by finding the parameter
        that minimizes the difference from the target y-value), a provided parameter, or the
        average of minimum and maximum logging y-values at the first x-value.

        Args:
            bearing_point (tuple[float, float], optional): A tuple of (x, y) coordinates to match
                for the growth line. Defaults to None.
            bearing_parameter (float, optional): A specific starting parameter for the growth line.
                Defaults to None.

        Returns:
            None

        Raises:
            ValueError: If min_logging_y_values or max_logging_y_values are not initialized.
        """
        if not self.min_logging_y_values.size or not self.max_logging_y_values.size:
            raise ValueError("Logging lines are not initialized")

        if bearing_point is not None:
            start_x, start_y = bearing_point
            min_y, max_y = self.min_logging_y_values[0], self.max_logging_y_values[0]
            min_diff = float("inf")
            best_param = min_y

            for param in np.arange(min_y, max_y, Settings.STEP_VALUE_GRAPH):
                predicted_y = self.line_manager.predict_value(TypeLine.GROWTH_LINE, start_x, param)
                diff = abs(predicted_y - start_y)
                if diff < min_diff:
                    min_diff = diff
                    best_param = param

            self.growth_line_start_value = best_param
        elif bearing_parameter is not None:
            self.growth_line_start_value = bearing_parameter
        else:
            self.growth_line_start_value = (self.min_logging_y_values[0] + self.max_logging_y_values[0]) / 2

    def get_growth_line_start_value(self) -> float:
        """Retrieve the starting value for the growth line.

        Ensures the growth line is initialized and returns its starting parameter.

        Returns:
            float: The starting parameter for the growth line.

        Raises:
            ValueError: If the growth line start value is not initialized.
        """
        if self.growth_line_y_values.size == 0:
            self.initialize_growth_line()
        if self.growth_line_start_value is None:
            raise ValueError("Growth line start value is not initialized")
        return self.growth_line_start_value

    def initialize_growth_line(self) -> None:
        """Initialize the growth line y-values.

        Generates y-values for the growth line using the GROWTH_LINE model and the current
        growth_line_start_value. Applies monotony correction to ensure valid predictions.

        Returns:
            None

        Raises:
            ValueError: If x_values are not initialized or growth_line_start_value is not set.
        """
        if self.x_values.size == 0:
            raise ValueError("x_values are not initialized")
        if self.growth_line_start_value is None:
            self.set_growth_line_start_value()
        self.growth_line_y_values = self.line_manager.predict_list_value(
            type_line=TypeLine.GROWTH_LINE, x_values=self.x_values, start_parameter=self.growth_line_start_value
        )
        if not isinstance(self.growth_line_y_values, np.ndarray):
            self.growth_line_y_values = np.array(self.growth_line_y_values, dtype=float)
        self.growth_line_y_values = fix_monotony(array=self.growth_line_y_values)

    def get_growth_line(self) -> list[float]:
        """Retrieve the y-values for the growth line.

        Ensures the growth line is initialized and returns its y-values.

        Returns:
            list[float]: The y-values for the growth line.

        Raises:
            ValueError: If the growth line is not initialized.
        """
        if self.growth_line_y_values.size == 0:
            self.initialize_growth_line()
        return self.growth_line_y_values.tolist()

    def get_planned_thinnings(self) -> list[dict[str, float]]:
        """Retrieve the list of planned thinning events.

        Returns a list of dictionaries, each containing the x-coordinate, past value, and new
        value for a thinning event.

        Returns:
            list[dict[str, float]]: A list of thinning event dictionaries with keys 'x',
                'past_value', and 'new_value'.

        Raises:
            ValueError: If planned_thinnings is not initialized.
        """
        if self.planned_thinnings is None:
            raise ValueError("Planned thinnings are not initialized")
        return self.planned_thinnings

    def get_thinning_track(self) -> dict[str, list[float]]:
        """Retrieve the thinning track data.

        Returns a dictionary with x and y values representing the thinning track.

        Returns:
            dict[str, list[float]]: A dictionary with keys 'x' and 'y', each mapping to a list
                of floats for the thinning track.

        Raises:
            ValueError: If the thinning track is not initialized.
        """
        if not self.thinning_track:
            raise ValueError("Thinning track is not initialized")
        return self.thinning_track

    def rewrite_thinning_event(self, index: int, item: dict[str, float]) -> None:
        """Rewrite a thinning event at the specified index.

        Updates the thinning event at the given index with new data, adds it via add_thinning,
        and reinitializes the thinning track to reflect the changes.

        Args:
            index (int): The index of the thinning event to rewrite.
            item (dict[str, float]): A dictionary with keys 'x', 'past_value', and 'new_value'
                representing the new thinning event data.

        Returns:
            None

        Raises:
            IndexError: If the index is out of range.
        """
        if not (0 <= index < len(self.planned_thinnings)):
            raise IndexError("Index out of range")
        self.planned_thinnings[index] = item
        self.add_thinning(date_thinning=item["x"], value_thinning=item["past_value"])
        self.initialize_track_thinning()

    def add_thinning(self, date_thinning: float, value_thinning: float) -> None:
        """Add a new thinning event.

        Inserts a new thinning event at the specified date with the given past value, sorted
        by date, updates the planned_thinnings list, runs a simulation from the date, and
        reinitializes the thinning track.

        Args:
            date_thinning (float): The x-coordinate (date) of the thinning event.
            value_thinning (float): The y-value (past value) before thinning.

        Returns:
            None

        Raises:
            ValueError: If required data (x_values, min_logging_y_values) is not initialized.
        """
        if not self.x_values.size or not self.min_logging_y_values.size:
            raise ValueError("Required data is not initialized")
        if self.planned_thinnings is None:
            self.planned_thinnings = []

        index = next(
            (i for i, event in enumerate(self.planned_thinnings) if event["x"] >= date_thinning),
            len(self.planned_thinnings),
        )

        old_value = value_thinning
        new_value = next(self.min_logging_y_values[i] for i, x in enumerate(self.x_values) if x >= date_thinning)

        self.planned_thinnings = self.planned_thinnings[:index]
        self.planned_thinnings.append({"x": date_thinning, "past_value": old_value, "new_value": new_value})

        from_end_simulation = self.simulation_thinning(start_date=date_thinning)
        self.planned_thinnings.extend(from_end_simulation)
        self.initialize_track_thinning()

    def correct_thinning(self, date_thinning: float, value_thinning: float) -> None:
        """Correct the new value of a thinning event at the specified date.

        Updates the new_value of the thinning event at the given date, recalculates the recovery
        line parameter to match the new value, runs a simulation from the date, and reinitializes
        the thinning track.

        Args:
            date_thinning (float): The x-coordinate (date) of the thinning event to correct.
            value_thinning (float): The new y-value after thinning.

        Returns:
            None

        Raises:
            ValueError: If planned_thinnings or x_values are not initialized, or if the thinning
                event is not found.
        """
        if self.planned_thinnings is None or not self.x_values.size:
            raise ValueError("Требуемые данные не инициализированы")

        index = next((i for i, event in enumerate(self.planned_thinnings) if event["x"] == date_thinning), None)
        if index is None:
            raise ValueError(f"Событие вырубки на дате {date_thinning} не найдено")

        self.planned_thinnings[index]["new_value"] = value_thinning

        x_before = self.x_values[self.x_values < date_thinning]
        min_diff = float("inf")
        best_param = 0
        for x in reversed(x_before):
            predicted = self.line_manager.predict_value(
                type_line=TypeLine.RECOVERY_LINE, x=date_thinning, start_parameter=x
            )
            diff = abs(predicted - value_thinning)
            if diff < min_diff:
                min_diff = diff
                best_param = x
            else:
                break

        from_end_simulation = self.simulation_thinning(start_date=date_thinning, parameter_predict=best_param)

        self.planned_thinnings = self.planned_thinnings[: index + 1] + from_end_simulation

        self.initialize_track_thinning()

    def delete_thinning(self, index: int) -> None:
        """Delete a thinning event at the specified index.

        Removes the thinning event at the given index, updates the next event's past_value
        using the growth or recovery line, and reinitializes the thinning track.

        Args:
            index (int): The index of the thinning event to delete.

        Returns:
            None

        Raises:
            IndexError: If the index is out of range.
        """
        if not (0 <= index < len(self.planned_thinnings)):
            raise IndexError("Index out of range")

        start_parameter = self.planned_thinnings[index - 1]["x"] if index > 0 else self.growth_line_start_value
        next_event = self.planned_thinnings[index + 1]
        new_x, new_value = next_event["x"], next_event["new_value"]

        type_line = TypeLine.GROWTH_LINE if index == 0 else TypeLine.RECOVERY_LINE
        next_value = self.line_manager.predict_value(type_line=type_line, x=new_x, start_parameter=start_parameter)

        del self.planned_thinnings[index]
        self.planned_thinnings[index] = {"x": new_x, "past_value": next_value, "new_value": new_value}
        self.initialize_track_thinning()

    def check_save_forest(self) -> None:
        """Ensure thinning events comply with forest protection limits.

        Removes thinning events that exceed the age limit for protective forests (age_thinning_save)
        or regular forests (age_thinning), keeping at least two events, and reinitializes the
        thinning track.

        Returns:
            None

        Raises:
            IndexError: If the planned_thinnings list has fewer than two events.
        """
        if len(self.planned_thinnings) < 2:
            raise IndexError("Planned thinnings list is too short")
        age_limit = (
            self.graph_data.age_thinning_save if self.graph_data.flag_save_forest else self.graph_data.age_thinning
        )
        while len(self.planned_thinnings) > 2 and self.planned_thinnings[-2]["x"] > age_limit:
            del self.planned_thinnings[-2]
        self.initialize_track_thinning()

    def _get_simulation_range(self, start_date: float | None) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Select the simulation range based on the start date.

        Returns arrays of x-values, growth line y-values, economic minimum y-values, and minimum
        logging y-values, filtered by start_date if provided.

        Args:
            start_date (float, optional): The starting date for the simulation range. Defaults to None.

        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: A tuple containing (x_values,
                growth_y_values, economic_y_values, logging_y_values).
        """
        if start_date is None:
            return self.x_values, self.growth_line_y_values, self.economic_min_y_values, self.min_logging_y_values
        mask = self.x_values >= start_date
        return (
            self.x_values[mask],
            self.growth_line_y_values[mask],
            self.economic_min_y_values[mask],
            self.min_logging_y_values[mask],
        )

    def _should_thin(
        self, x: float, current_value: float, bearing_y: float, economic_y: float, cutting_limit: float
    ) -> bool:
        """Determine if a thinning event should occur at the given point.

        Checks if the current value meets the conditions for thinning based on growth line,
        economic minimum, and cutting age limits.

        Args:
            x (float): The x-coordinate (date) to check.
            current_value (float): The current y-value (e.g., from growth or recovery line).
            bearing_y (float): The y-value of the growth line at x.
            economic_y (float): The y-value of the economic minimum line at x.
            cutting_limit (float): The maximum age for thinning (age_thinning or age_thinning_save).

        Returns:
            bool: True if thinning should occur, False otherwise.
        """
        return (
            current_value >= bearing_y
            and x > self.graph_data.x_min_economic
            and current_value >= economic_y
            and x <= cutting_limit
        )

    def simulation_thinning(
        self, start_date: float | None = None, parameter_predict: float | None = None
    ) -> list[dict[str, float]]:
        """Simulate thinning events from a starting date.

        Generates a list of thinning events based on growth and recovery line predictions,
        considering economic minimum and age limits. Updates planned_thinnings if not previously set.

        Args:
            start_date (float, optional): The starting date for the simulation. Defaults to None (uses full range).
            parameter_predict (float, optional): The starting parameter for recovery line predictions.
                Defaults to None (uses growth_line_start_value or first x-value).

        Returns:
            list[dict[str, float]]: A list of thinning event dictionaries with keys 'x',
                'past_value', and 'new_value'.

        Raises:
            ValueError: If required data (x_values, growth_line_y_values, etc.) is not initialized.
        """
        if not all(
            [
                self.x_values.size,
                self.growth_line_y_values.size,
                self.economic_min_y_values.size,
                self.min_logging_y_values.size,
            ]
        ):
            raise ValueError("Required data is not initialized")

        x_values, bearing_y, economic_y, logging_y = self._get_simulation_range(start_date)
        x_values = x_values[x_values <= self.graph_data.age_thinning]

        cutting_limit = (
            self.graph_data.age_thinning_save if self.graph_data.flag_save_forest else self.graph_data.age_thinning
        )
        thinnings = []

        start_parameter = self.growth_line_start_value if start_date is None else (parameter_predict or x_values[0])
        flag_thinning = start_date is not None

        for i, x in enumerate(x_values):
            current_value = (
                bearing_y[i]
                if not flag_thinning
                else self.line_manager.predict_value(TypeLine.RECOVERY_LINE, x, start_parameter)
            )
            current_value = max(current_value, logging_y[i])

            if self._should_thin(x, current_value, bearing_y[i], economic_y[i], cutting_limit):
                thinnings.append({"x": x, "past_value": current_value, "new_value": logging_y[i]})
                flag_thinning = True
                start_parameter = x

        final_x = self.x_values[-1]
        final_value = (
            bearing_y[-1]
            if not flag_thinning
            else self.line_manager.predict_value(TypeLine.RECOVERY_LINE, final_x, start_parameter)
        )
        final_value = max(final_value, self.min_logging_y_values[-1])
        thinnings.append({"x": final_x, "past_value": final_value, "new_value": 0.000000000001})

        if self.planned_thinnings is None:
            self.planned_thinnings = thinnings

        return thinnings

    def initialize_track_thinning(self) -> None:
        """Initialize the thinning track based on planned thinning events.

        Generates x and y values for the thinning track, following the growth line until a
        thinning event, then using the recovery line and adding vertical cuts for thinning events
        to represent the drop from past_value to new_value.

        Returns:
            None

        Raises:
            ValueError: If planned_thinnings is not initialized.
        """
        if not self.planned_thinnings:
            raise ValueError("Planned thinnings are not initialized")

        track_x, track_y = [], []
        start_parameter = self.growth_line_start_value
        current_value = self.growth_line_start_value
        flag_thinning = False
        thinning_index = 0

        for i, x in enumerate(self.x_values):
            current_value = (
                self.growth_line_y_values[i]
                if not flag_thinning
                else max(
                    self.line_manager.predict_value(
                        type_line=TypeLine.RECOVERY_LINE, x=x, start_parameter=start_parameter
                    ),
                    self.min_logging_y_values[i],
                )
            )

            track_x.append(x)
            track_y.append(current_value)

            if thinning_index < len(self.planned_thinnings) and x >= self.planned_thinnings[thinning_index]["x"]:
                flag_thinning = True
                past_value = self.planned_thinnings[thinning_index]["past_value"]
                new_value = self.planned_thinnings[thinning_index]["new_value"]
                current_value = new_value
                thinning_index += 1

                if thinning_index < len(self.planned_thinnings):
                    next_true_value = self.planned_thinnings[thinning_index]["past_value"]
                    next_date = self.planned_thinnings[thinning_index]["x"]
                    min_diff = float("inf")
                    for j in range(i, -1, -1):
                        predicted = self.line_manager.predict_value(
                            type_line=TypeLine.RECOVERY_LINE, x=next_date, start_parameter=self.x_values[j]
                        )
                        diff = abs(predicted - next_true_value)
                        if diff < min_diff:
                            min_diff = diff
                            start_parameter = self.x_values[j]
                        else:
                            break

                y_cut = np.arange(past_value, new_value, -Settings.STEP_VALUE_GRAPH)
                x_cut = np.full_like(y_cut, x)
                track_x.extend(x_cut)
                track_y.extend(y_cut)

        self.thinning_track = {"x": track_x, "y": track_y}

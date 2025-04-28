"""Module for managing graph data and simulations in forest growth and thinning.

This module defines the Graph class, which serves as the primary interface for handling
graph metadata, line models, thinning simulations, and serialization. It integrates
GraphData for metadata, LineManager for line predictions, ThinningSimulator for thinning
simulations, and GraphSerializer for data loading/saving in forest growth simulations.

Dependencies:
    - GraphData: Dataclass for storing graph metadata.
    - LineManager: Class for managing Line objects.
    - ThinningSimulator: Class for simulating forest thinning.
    - GraphSerializer: Class for serializing/deserializing graph data.
    - TypeLine: Enum defining types of lines (e.g., GROWTH_LINE, RECOVERY_LINE).
    - Settings: Class containing configuration constants (e.g., STEP_PLOTTING_GRAPH).
"""

from .GraphData import GraphData
from .LineManager import LineManager
from .ThinningSimulator import ThinningSimulator
from .GraphSerializer import GraphSerializer
from ...background_information.TypeLine import TypeLine
from ...background_information.Settings import Settings


class Graph:
    """Primary interface for managing graph data and simulations in forest growth.

    Integrates GraphData for metadata, LineManager for line predictions, ThinningSimulator
    for thinning simulations, and GraphSerializer for data loading/saving. Provides methods
    for initializing graphs, managing lines, predicting values, and simulating thinning
    events in forest growth and thinning simulations.

    Attributes:
        data (GraphData): The metadata of the graph, including area, breed, and min/max values.
        line_manager (LineManager): The manager for Line objects associated with TypeLine enums.
        thinning_simulator (ThinningSimulator): The simulator for thinning events.
        serializer (GraphSerializer): The serializer for loading/saving graph data.
    """

    def __init__(self) -> None:
        """Initialize an empty Graph with default components.

        Sets up the Graph with an empty GraphData instance and new instances of LineManager,
        ThinningSimulator, and GraphSerializer.

        Returns:
            None
        """
        self.data = GraphData(name="", area="", breed="", condition="", age_thinning=0.0, age_thinning_save=0.0)
        self.line_manager = LineManager()
        self.thinning_simulator = ThinningSimulator(graph_data=self.data, line_manager=self.line_manager)
        self.serializer = GraphSerializer(graph_data=self.data, line_manager=self.line_manager)

    def initialize_model(
        self,
        name: str,
        area: str,
        breed: str,
        condition: str,
        age_thinning: float,
        age_thinning_save: float,
        flag_save_forest: bool = False,
    ) -> None:
        """Initialize the Graph with specific metadata and reset components.

        Creates a new GraphData instance with the provided metadata and reinitializes
        LineManager, ThinningSimulator, and GraphSerializer with the new data.

        Args:
            name (str): The name of the graph (e.g., file name).
            area (str): The name of the area associated with the graph.
            breed (str): The name of the breed associated with the graph.
            condition (str): The name of the condition associated with the graph.
            age_thinning (float): The age of thinning for the breed.
            age_thinning_save (float): The age of thinning for protective forests.
            flag_save_forest (bool, optional): Flag indicating protective forest mode. Defaults to False.

        Returns:
            None
        """
        self.data = GraphData(
            name=name,
            area=area,
            breed=breed,
            condition=condition,
            age_thinning=age_thinning,
            age_thinning_save=age_thinning_save,
            flag_save_forest=flag_save_forest,
        )
        self.line_manager = LineManager()
        self.thinning_simulator = ThinningSimulator(graph_data=self.data, line_manager=self.line_manager)
        self.serializer = GraphSerializer(graph_data=self.data, line_manager=self.line_manager)

    def get_min_max_value(self) -> tuple[float, float, float, float]:
        """Retrieve the minimum and maximum x and y values for plotting.

        Delegates to GraphData.get_min_max_value to return the x_min, x_max, y_min, and y_max values.

        Returns:
            tuple[float, float, float, float]: A tuple containing (x_min, x_max, y_min, y_max).

        Raises:
            ValueError: If any of x_min, x_max, y_min, or y_max is None in GraphData.
        """
        return self.data.get_min_max_value()

    def initialize_base_line_graph(
        self, x_start: float | None = None, x_end: float | None = None, step: float | None = None
    ) -> None:
        """Initialize base lines for the graph (minimum/maximum logging, economic minimum).

        Delegates to ThinningSimulator.initialize_base_line_graph to generate base lines.

        Args:
            x_start (float, optional): Starting x-value for the range. Defaults to None (uses GraphData.x_min).
            x_end (float, optional): Ending x-value for the range. Defaults to None (uses GraphData.x_max).
            step (float, optional): Step size for x-values. Defaults to None (uses ThinningSimulator.step).

        Returns:
            None

        Raises:
            ValueError: If required data or line models are not initialized.
        """
        self.thinning_simulator.initialize_base_line_graph(x_start=x_start, x_end=x_end, step=step)

    def set_flag_save_forest(self, flag_save_forest: bool = False) -> None:
        """Set the protective forest flag in GraphData.

        Updates the flag_save_forest attribute to indicate whether the forest is in protective mode.

        Args:
            flag_save_forest (bool, optional): Flag indicating protective forest mode. Defaults to False.

        Returns:
            None
        """
        self.data.flag_save_forest = flag_save_forest

    def get_base_lines_graph(self) -> dict[str, list[float]]:
        """Retrieve base line data for the graph.

        Delegates to ThinningSimulator.get_base_lines_graph to return x and y values for
        minimum logging, maximum logging, and economic minimum lines.

        Returns:
            dict[str, list[float]]: A dictionary with keys 'list_value_x', 'list_value_y_min_logging',
                'list_value_y_max_logging', and 'list_value_y_min_economic', each mapping to a list of floats.

        Raises:
            ValueError: If base lines are not initialized.
        """
        return self.thinning_simulator.get_base_lines_graph()

    def set_bearing_parameter(
        self, bearing_point: tuple[float, float] | None = None, bearing_parameter: float | None = None
    ) -> None:
        """Set the starting value for the growth line.

        Delegates to ThinningSimulator.set_growth_line_start_value to set the growth line's
        starting parameter based on a bearing point or provided parameter.

        Args:
            bearing_point (tuple[float, float], optional): A tuple of (x, y) coordinates to match
                for the growth line. Defaults to None.
            bearing_parameter (float, optional): A specific starting parameter for the growth line.
                Defaults to None.

        Returns:
            None

        Raises:
            ValueError: If required data is not initialized.
        """
        self.thinning_simulator.set_growth_line_start_value(
            bearing_point=bearing_point, bearing_parameter=bearing_parameter
        )

    def get_bearing_parameter(self) -> float:
        """Retrieve the starting value for the growth line.

        Delegates to ThinningSimulator.get_growth_line_start_value to return the growth line's
        starting parameter.

        Returns:
            float: The starting parameter for the growth line.

        Raises:
            ValueError: If the growth line start value is not initialized.
        """
        return self.thinning_simulator.get_growth_line_start_value()

    def initialize_bearing_line(self) -> None:
        """Initialize the growth line y-values.

        Delegates to ThinningSimulator.initialize_growth_line to generate y-values for the
        growth line.

        Returns:
            None

        Raises:
            ValueError: If required data is not initialized.
        """
        self.thinning_simulator.initialize_growth_line()

    def get_bearing_line(self) -> list[float]:
        """Retrieve the y-values for the growth line.

        Delegates to ThinningSimulator.get_growth_line to return the growth line's y-values.

        Returns:
            list[float]: The y-values for the growth line.

        Raises:
            ValueError: If the growth line is not initialized.
        """
        return self.thinning_simulator.get_growth_line()

    def load_reference_info(
        self, code_area: str | None = None, code_breed: str | None = None, code_condition: str | None = None
    ) -> None:
        """Update reference codes for area, breed, and condition.

        Delegates to GraphData.update_codes to update code_area, code_breed, and code_condition.

        Args:
            code_area (str, optional): The new area code. Defaults to None.
            code_breed (str, optional): The new breed code. Defaults to None.
            code_condition (str, optional): The new condition code. Defaults to None.

        Returns:
            None
        """
        self.data.update_codes(code_area=code_area, code_breed=code_breed, code_condition=code_condition)

    def load_graph_from_tar(self) -> None:
        """Load graph data from a tar archive.

        Delegates to GraphSerializer.load_graph_from_tar to load graph data from a tar archive.

        Returns:
            None

        Raises:
            FileNotFoundError: If the tar file does not exist.
            ValueError: If the JSON data is invalid or missing required keys.
            tarfile.TarError: If there is an error reading the tar archive.
            json.JSONDecodeError: If the JSON file cannot be decoded.
        """
        self.serializer.load_graph_from_tar()

    def fit_models(self) -> None:
        """Fit regression models for all Line objects.

        Delegates to LineManager.fit_models to train regression models for all lines.

        Returns:
            None
        """
        self.line_manager.fit_models()

    def clear_train_data(self) -> None:
        """Clear training data for all Line objects.

        Delegates to LineManager.clear_train_data to free memory used by training data.

        Returns:
            None
        """
        self.line_manager.clear_train_data()

    def save_graph(self) -> None:
        """Save graph data and line models to JSON and pickle files.

        Delegates to GraphSerializer.save_graph to serialize graph metadata and line models.

        Returns:
            None
        """
        self.serializer.save_graph()

    def load_graph(self) -> None:
        """Load graph data and line models from JSON and pickle files.

        Delegates to GraphSerializer.load_graph to deserialize graph metadata and line models.

        Returns:
            None

        Raises:
            FileNotFoundError: If the JSON file does not exist.
            ValueError: If the JSON data is invalid or the graph name does not match.
        """
        self.serializer.load_graph()

    def predict_value(self, type_line: TypeLine, x: float, start_parameter: float = 0) -> float:
        """Predict a single y-value for a given x-coordinate and TypeLine.

        Delegates to LineManager.predict_value to predict a y-value using the specified line model.

        Args:
            type_line (TypeLine): The type of line to predict (e.g., GROWTH_LINE, RECOVERY_LINE).
            x (float): The x-coordinate for the prediction.
            start_parameter (float, optional): Starting parameter for the prediction, must be 0
                for non-growth/recovery lines. Defaults to 0.

        Returns:
            float: The predicted y-value.

        Raises:
            ValueError: If the TypeLine is not found or if start_parameter is non-zero for
                non-growth/recovery lines.
        """
        return self.line_manager.predict_value(type_line=type_line, x=x, start_parameter=start_parameter)

    def predict_list_value(self, type_line: TypeLine, x_values: list[float], start_parameter: float = 0) -> list[float]:
        """Predict y-values for a list of x-coordinates and a TypeLine.

        Delegates to LineManager.predict_list_value to predict y-values using the specified line model.

        Args:
            type_line (TypeLine): The type of line to predict (e.g., GROWTH_LINE, RECOVERY_LINE).
            x_values (list[float]): The list of x-coordinates for predictions.
            start_parameter (float, optional): Starting parameter for the prediction, must be 0
                for non-growth/recovery lines. Defaults to 0.

        Returns:
            list[float]: A list of predicted y-values.

        Raises:
            ValueError: If the TypeLine is not found or if start_parameter is non-zero for
                non-growth/recovery lines.
        """
        return self.line_manager.predict_list_value(
            type_line=type_line, x_values=x_values, start_parameter=start_parameter
        )

    def predict_line(
        self,
        type_line: TypeLine,
        start_x: float | None = None,
        end_x: float | None = None,
        step: float | None = None,
        start_parameter: float = 0,
    ) -> tuple[list[float], list[float]]:
        """Generate x and y values for a TypeLine over a range of x-coordinates.

        Delegates to LineManager.predict_line to generate x and y values for the specified line model.
        Uses default values for start_x, end_x, and step based on GraphData and Settings.

        Args:
            type_line (TypeLine): The type of line to predict (e.g., GROWTH_LINE, RECOVERY_LINE).
            start_x (float, optional): Starting x-coordinate for the range. Defaults to x_min_economic
                for ECONOMIC_MIN_LINE, otherwise x_min.
            end_x (float, optional): Ending x-coordinate for the range. Defaults to x_max.
            step (float, optional): Step size between x-coordinates. Defaults to Settings.STEP_PLOTTING_GRAPH.
            start_parameter (float, optional): Starting parameter for the prediction, must be 0
                for non-growth/recovery lines. Defaults to 0.

        Returns:
            tuple[list[float], list[float]]: A tuple of (x_values, y_values) for the predicted line.

        Raises:
            ValueError: If the TypeLine is not found, if start_parameter is non-zero for
                non-growth/recovery lines, or if start_x is greater than or equal to end_x.
        """
        start_x = start_x or (self.data.x_min_economic if type_line == TypeLine.ECONOMIC_MIN_LINE else self.data.x_min)
        end_x = end_x or self.data.x_max
        step = step or Settings.STEP_PLOTTING_GRAPH
        return self.line_manager.predict_line(
            type_line=type_line, start_x=start_x, end_x=end_x, step=step, start_parameter=start_parameter
        )

    def get_list_record_planned_thinning(self) -> list[dict[str, float]]:
        """Retrieve the list of planned thinning events.

        Delegates to ThinningSimulator.get_planned_thinnings to return the list of thinning events.

        Returns:
            list[dict[str, float]]: A list of thinning event dictionaries with keys 'x',
                'past_value', and 'new_value'.

        Raises:
            ValueError: If planned_thinnings is not initialized.
        """
        return self.thinning_simulator.get_planned_thinnings()

    def get_list_value_track_thinning(self) -> dict[str, list[float]]:
        """Retrieve the thinning track data.

        Delegates to ThinningSimulator.get_thinning_track to return the thinning track data.

        Returns:
            dict[str, list[float]]: A dictionary with keys 'x' and 'y', each mapping to a list
                of floats for the thinning track.

        Raises:
            ValueError: If the thinning track is not initialized.
        """
        return self.thinning_simulator.get_thinning_track()

    def rewrite_item_record_planed_thinning(self, index: int, item: dict[str, float]) -> None:
        """Rewrite a thinning event at the specified index.

        Delegates to ThinningSimulator.rewrite_thinning_event to update the thinning event.

        Args:
            index (int): The index of the thinning event to rewrite.
            item (dict[str, float]): A dictionary with keys 'x', 'past_value', and 'new_value'
                representing the new thinning event data.

        Returns:
            None

        Raises:
            IndexError: If the index is out of range.
        """
        self.thinning_simulator.rewrite_thinning_event(index=index, item=item)

    def add_thinning(self, date_thinning: float, value_thinning: float) -> None:
        """Add a new thinning event.

        Delegates to ThinningSimulator.add_thinning to insert a new thinning event.

        Args:
            date_thinning (float): The x-coordinate (date) of the thinning event.
            value_thinning (float): The y-value (past value) before thinning.

        Returns:
            None

        Raises:
            ValueError: If required data is not initialized.
        """
        self.thinning_simulator.add_thinning(date_thinning=date_thinning, value_thinning=value_thinning)

    def correct_thinning(self, date_thinning: float, value_thinning: float) -> None:
        """Correct the new value of a thinning event at the specified date.

        Delegates to ThinningSimulator.correct_thinning to update the thinning event's new value.

        Args:
            date_thinning (float): The x-coordinate (date) of the thinning event to correct.
            value_thinning (float): The new y-value after thinning.

        Returns:
            None

        Raises:
            ValueError: If required data is not initialized or the thinning event is not found.
        """
        self.thinning_simulator.correct_thinning(date_thinning=date_thinning, value_thinning=value_thinning)

    def delete_thinning(self, index: int) -> None:
        """Delete a thinning event at the specified index.

        Delegates to ThinningSimulator.delete_thinning to remove the thinning event.

        Args:
            index (int): The index of the thinning event to delete.

        Returns:
            None

        Raises:
            IndexError: If the index is out of range.
        """
        self.thinning_simulator.delete_thinning(index=index)

    def check_graph_save_forest(self) -> None:
        """Ensure thinning events comply with forest protection limits.

        Delegates to ThinningSimulator.check_save_forest to enforce thinning age limits.

        Returns:
            None

        Raises:
            IndexError: If the planned_thinnings list has fewer than two events.
        """
        self.thinning_simulator.check_save_forest()

    def simulation_thinning(
        self, start_date: float | None = None, parameter_predict: float | None = None
    ) -> list[dict[str, float]]:
        """Simulate thinning events from a starting date.

        Delegates to ThinningSimulator.simulation_thinning to generate thinning events and
        updates the planned_thinnings in ThinningSimulator.

        Args:
            start_date (float, optional): The starting date for the simulation. Defaults to None.
            parameter_predict (float, optional): The starting parameter for recovery line predictions.
                Defaults to None.

        Returns:
            list[dict[str, float]]: A list of thinning event dictionaries with keys 'x',
                'past_value', and 'new_value'.

        Raises:
            ValueError: If required data is not initialized.
        """
        thinnings = self.thinning_simulator.simulation_thinning(
            start_date=start_date, parameter_predict=parameter_predict
        )
        self.thinning_simulator.planned_thinnings = thinnings
        return thinnings

    def initialize_track_thinning(self) -> None:
        """Initialize the thinning track based on planned thinning events.

        Delegates to ThinningSimulator.initialize_track_thinning to generate the thinning track.

        Returns:
            None

        Raises:
            ValueError: If planned_thinnings is not initialized.
        """
        self.thinning_simulator.initialize_track_thinning()

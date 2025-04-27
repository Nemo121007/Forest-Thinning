"""Module for managing graph data and prediction models in a reference data system.

This module provides the Graph class, which handles graph data associated with areas, breeds,
and conditions, storing multiple line models (e.g., growth, logging) and supporting data loading,
model fitting, prediction, and serialization.
"""

import json
import tarfile
import joblib
import numpy as np
from ...background_information.Paths import Paths

from .Line import Line
from ...background_information.TypeLine import TypeLine
from ...background_information.Settings import Settings
from ...background_information.General_functions import fix_monotony, cast_coordinates_point


class Graph:
    """A class for managing graph data and associated prediction models.

    Stores graph metadata (area, breed, condition) and a collection of Line models for
    different line types (e.g., growth, logging). Supports loading data from tar files,
    fitting polynomial regression models, making predictions, and saving/loading model state.

    Attributes:
        name (str): The name of the graph (file name).
        dict_line (dict[TypeLine, Line]): Dictionary mapping line types to Line models.
        area (str): The name of the area.
        code_area (str): The code for the area.
        breed (str): The name of the breed.
        code_breed (str): The code for the breed.
        condition (str): The name of the condition.
        code_condition (str): The code for the condition.
        age_thinning (float): The age of thinning for the breed.
        age_thinning_save (float): The age of thinning for protective forests.
        flag_save_forest (bool): Flag indicating protective forest mode.
        x_max (float): Maximum x-value for the graph.
        x_min (float): Minimum x-value for the graph.
        y_max (float): Maximum y-value for the graph.
        y_min (float): Minimum y-value for the graph.
        x_min_economic (float): Minimum x-value for the economic minimum line.
    """

    def __init__(self) -> None:
        """Initialize an empty Graph instance.

        Sets up default values for all attributes, with an empty dictionary for line models.

        Returns:
            None
        """
        self.name: str = None
        self.dict_line: dict[TypeLine, Line] = {}
        self.area: str = None
        self.code_area: str = None
        self.breed: str = None
        self.code_breed: str = None
        self.condition: str = None
        self.code_condition: str = None
        self.age_thinning: float = None
        self.age_thinning_save: float = None
        self.flag_save_forest: bool = False
        self.x_max: float = None
        self.x_min: float = None
        self.y_max: float = None
        self.y_min: float = None
        self.x_min_economic: float = None
        self.list_value_x: list[float] = None

        self.step: float = Settings.STEP_PLOTTING_GRAPH
        self.list_value_y_min_logging: list[float] = None
        self.list_value_y_max_logging: list[float] = None
        self.list_value_y_min_economic: list[float] = None

        self.bearing_value_parameter: float = None
        self.bearing_value_y_line: list[float] = None

        self.list_value_track_thinning: dict[str, list[float]] = None
        self.list_record_planned_thinning: list[dict[str, float]] = None

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
        """Initialize the graph with metadata and reset line models.

        Sets up the graph name, area, breed, condition, thinning ages, and forest mode,
        clearing any existing line models.

        Args:
            name (str): The name of the graph (file name).
            area (str): The name of the area.
            breed (str): The name of the breed.
            condition (str): The name of the condition.
            age_thinning (float): The age of thinning for the breed.
            age_thinning_save (float): The age of thinning for protective forests.
            flag_save_forest (bool, optional): Indicates protective forest mode. Defaults to False.

        Returns:
            None
        """
        self.__init__()
        self.name: str = name
        self.dict_line: dict[TypeLine, Line] = {}
        self.area: str = area
        self.code_area: str = None
        self.breed: str = breed
        self.code_breed: str = None
        self.condition: str = condition
        self.code_condition: str = None
        self.age_thinning: float = age_thinning
        self.age_thinning_save: float = age_thinning_save
        self.flag_save_forest: bool = flag_save_forest
        self.x_max: float = None
        self.x_min: float = None
        self.y_max: float = None
        self.y_min: float = None
        self.x_min_economic: float = None

    def get_min_max_value(self) -> tuple[float, float, float, float]:
        """Retrieve the minimum and maximum x and y values for the graph.

        Returns the range limits for plotting the graph data.

        Returns:
            tuple[float, float, float, float]: A tuple of (x_min, x_max, y_min, y_max).

        Raises:
            ValueError: If any of x_min, x_max, y_min, or y_max is not set.
        """
        if self.x_min is None or self.x_max is None or self.y_min is None or self.y_max is None:
            raise ValueError("Graph is not loaded")
        return self.x_min, self.x_max, self.y_min, self.y_max

    def initialize_base_line_graph(self, x_start: float = None, x_end: float = None, step: float = None) -> None:
        """Initialize base lines for the graph (logging and economic minimum).

        Generates x-values over a range and predicts y-values for minimum logging, maximum
        logging, and economic minimum lines using the corresponding Line models.

        Args:
            x_start (float, optional): Starting x-value for the range. Defaults to x_min.
            x_end (float, optional): Ending x-value for the range. Defaults to x_max.
            step (float, optional): Step size between x-values. Defaults to self.step.

        Returns:
            None

        Raises:
            Exception: If the graph is not loaded (x_min or x_max unset) or required line models are missing.
        """
        if self.x_max is None or self.x_min is None:
            raise Exception("Graph is not loaded or not initialize")
        if (
            TypeLine.MIN_LEVEL_LOGGING not in self.dict_line
            or TypeLine.MAX_LEVEL_LOGGING not in self.dict_line
            or TypeLine.ECONOMIC_MIN_LINE not in self.dict_line
        ):
            raise Exception("Graph is not loaded model predicted line")
        if x_start is None:
            x_start = self.x_min
        if x_end is None:
            x_end = self.x_max
        if step is None:
            step = self.step

        x_max, _ = cast_coordinates_point(self.x_max, 0)
        x_min, _ = cast_coordinates_point(self.x_min, 0)
        self.list_value_x = np.arange(x_min, x_max + step, step).tolist()

        self.list_value_y_min_logging = self.predict_list_value(
            type_line=TypeLine.MIN_LEVEL_LOGGING, X=self.list_value_x, start_parameter=0
        )
        self.list_value_y_min_logging = fix_monotony(array=self.list_value_y_min_logging)

        self.list_value_y_max_logging = self.predict_list_value(
            type_line=TypeLine.MAX_LEVEL_LOGGING, X=self.list_value_x, start_parameter=0
        )
        self.list_value_y_max_logging = fix_monotony(array=self.list_value_y_max_logging)

        self.list_value_y_min_economic = self.predict_list_value(
            type_line=TypeLine.ECONOMIC_MIN_LINE, X=self.list_value_x, start_parameter=0
        )
        self.list_value_y_min_economic = fix_monotony(array=self.list_value_y_min_economic)
        x_min_economic, _ = cast_coordinates_point(self.x_min_economic, 0)
        for i in range(len(self.list_value_x)):
            if self.list_value_x[i] < x_min_economic:
                self.list_value_y_min_economic[i] = self.list_value_y_max_logging[i]

    def set_flag_save_forest(self, flag_save_forest: bool = False) -> None:
        """Set the protective forest mode flag for the graph.

        Updates the flag to enable or disable protective forest mode, which affects thinning
        age limits in simulations.

        Args:
            flag_save_forest (bool, optional): Indicates protective forest mode. Defaults to False.

        Returns:
            None
        """
        self.flag_save_forest = flag_save_forest

    def get_base_lines_graph(self) -> dict[str, list[float]]:
        """Retrieve the x-values and y-values for base lines (logging and economic minimum).

        Returns a dictionary containing x-values and predicted y-values for minimum logging,
        maximum logging, and economic minimum lines.

        Returns:
            dict[str, list[float]]: A dictionary with keys:
                - 'list_value_x': List of x-values.
                - 'list_value_y_min_logging': List of y-values for minimum logging line.
                - 'list_value_y_max_logging': List of y-values for maximum logging line.
                - 'list_value_y_min_economic': List of y-values for economic minimum line.

        Raises:
            ValueError: If the base lines have not been initialized.
        """
        return {
            "list_value_x": self.list_value_x,
            "list_value_y_min_logging": self.list_value_y_min_logging,
            "list_value_y_max_logging": self.list_value_y_max_logging,
            "list_value_y_min_economic": self.list_value_y_min_economic,
        }

    def set_bearing_parameter(self, bearing_point: tuple[float, float] = None, bearing_parameter: float = None) -> None:
        """Set the bearing parameter for the growth line.

        Assigns the bearing parameter either as the provided value, from a bearing point by
        finding the starting parameter that minimizes the difference between predicted and
        actual y-values, or as the average of the minimum and maximum logging lines’ initial
        y-values if neither is provided.

        Args:
            bearing_point (tuple[float, float], optional): A tuple of (x, y) coordinates for
                the bearing point. If provided, the parameter is calculated to minimize the
                difference from the growth line prediction. Defaults to None.
            bearing_parameter (float, optional): The bearing parameter value. If provided,
                used directly. Defaults to None.

        Returns:
            None

        Raises:
            ValueError: If the logging lines’ y-values are not initialized.
        """
        if bearing_point is not None:
            start_x = bearing_point[0]
            start_y = bearing_point[1]
            min_y = self.list_value_y_min_logging[0]
            max_y = self.list_value_y_max_logging[0]

            min_deferent = max_y
            for j in np.arange(start=min_y, stop=max_y, step=Settings.STEP_VALUE_GRAPH):
                predict_y = self.predict_value(type_line=TypeLine.GROWTH_LINE, X=start_x, start_parameter=j)
                different = abs(predict_y - start_y)
                if different <= min_deferent:
                    min_deferent = different
                else:
                    self.bearing_value_parameter = j
                    return
        elif bearing_parameter is not None:
            self.bearing_value_parameter = bearing_parameter
        else:
            self.bearing_value_parameter = (self.list_value_y_min_logging[0] + self.list_value_y_max_logging[0]) / 2

    def get_bearing_parameter(self) -> float:
        """Retrieve the current bearing parameter for the growth line.

        Returns the bearing parameter value used for growth line predictions, initializing
        the bearing line if necessary to ensure the parameter is set.

        Returns:
            float: The current bearing parameter value.

        Raises:
            ValueError: If the bearing parameter cannot be initialized due to missing data (e.g.,
            uninitialized x-values or logging lines).
        """
        if self.bearing_value_y_line is None:
            self.initialize_bearing_line()
        return self.bearing_value_parameter

    def initialize_bearing_line(self) -> None:
        """Initialize the bearing line for growth prediction.

        Sets up the bearing line by predicting y-values for the growth line using the
        current bearing parameter across the x-value range.

        Returns:
            None

        Raises:
            ValueError: If the x-values or bearing parameter are not initialized.
        """
        if self.bearing_value_parameter is None:
            self.set_bearing_parameter()
        self.bearing_value_y_line = self.predict_list_value(
            type_line=TypeLine.GROWTH_LINE, X=self.list_value_x, start_parameter=self.bearing_value_parameter
        )
        self.bearing_value_y_line = fix_monotony(array=self.bearing_value_y_line)

    def get_bearing_line(self) -> list[float]:
        """Retrieve the y-values of the bearing line.

        Returns the bearing line’s y-values, initializing the line if not already set.

        Returns:
            list[float]: The y-values of the bearing line.

        Raises:
            ValueError: If the bearing line cannot be initialized due to missing data.
        """
        self.initialize_bearing_line()
        return self.bearing_value_y_line

    def load_reference_info(self, code_area: str = None, code_breed: str = None, code_condition: str = None):
        """Update area, breed, and condition codes if provided.

        Sets the codes for area, breed, and condition, leaving unchanged if None.

        Args:
            code_area (str, optional): The code for the area. Defaults to None.
            code_breed (str, optional): The code for the breed. Defaults to None.
            code_condition (str, optional): The code for the condition. Defaults to None.

        Returns:
            None
        """
        if code_area is not None:
            self.code_area = code_area
        if code_breed is not None:
            self.code_breed = code_breed
        if code_condition is not None:
            self.code_condition = code_condition

    def load_graph_from_tar(self):
        """Load graph data from a tar file.

        Reads a JSON file from a tar archive, extracts line data, and populates line models
        with x and y values, updating min/max ranges.

        Returns:
            None

        Raises:
            Exception: If an error occurs while reading the tar file or parsing JSON data.
            KeyError: If the JSON data lacks the 'datasetColl' key.
        """
        tar_path = Paths.DATA_DIRECTORY / f"{self.name}.tar"

        try:
            with tarfile.open(tar_path, "r") as tar_ref:
                file_member = tar_ref.getmember(f"{self.name}/wpd.json")
                with tar_ref.extractfile(file_member) as file:
                    data = json.load(file)
                if "datasetColl" not in data:
                    raise KeyError("Key 'datasetColl' is missing in the JSON data")

                data_list = list(data["datasetColl"])
                data_list.sort(key=lambda x: x["name"])

                for i in range(len(data_list)):
                    line = dict(data_list[i])
                    self._load_data_line_one_line(line)

        except Exception as e:
            raise Exception(f"Error read data: {e}")

    def _load_data_line_one_line(self, line: dict):
        """Load data for a single line from JSON data.

        Processes a line data, creates or updates a Line model, and updates min/max ranges.

        Args:
            line (dict): Dictionary containing line data with name and x/y values.

        Returns:
            None

        Raises:
            ValueError: If the number of x and y values does not match.
        """
        all_x = []
        all_y = []

        for item in line["data"]:
            all_x.append(item["value"][0])
            all_y.append(item["value"][1])

        if len(all_x) != len(all_y):
            raise ValueError("The number of arguments X and Y does not match")

        item = Line()
        name_line = TypeLine.give_enum_from_value(value=line["name"])

        # Для построения графика достаточно MIN_LEVEL_LOGGING,
        # MAX_LEVEL_LOGGING, ECONOMIC_MIN_LINE, GROWTH_LINE и RECOVERY_LINE
        if (
            name_line == TypeLine.MIN_LEVEL_LOGGING
            or name_line == TypeLine.MAX_LEVEL_LOGGING
            or name_line == TypeLine.ECONOMIC_MIN_LINE
        ):
            item.load_info(type_line=name_line)
            self.dict_line[name_line] = item
            if name_line == TypeLine.ECONOMIC_MIN_LINE:
                if self.x_min_economic is None or self.x_min_economic > min(all_x):
                    self.x_min_economic = min(all_x)
        elif name_line == TypeLine.GROWTH_LINE or name_line == TypeLine.RECOVERY_LINE:
            if name_line in self.dict_line:
                item = self.dict_line[name_line]
            else:
                item.load_info(type_line=name_line)
                self.dict_line[name_line] = item
        else:
            return
        item.append_data(X=all_x, Y=all_y)

        if self.x_max is None or self.x_max < max(all_x):
            self.x_max = max(all_x)
        if self.x_min is None or self.x_min > min(all_x):
            self.x_min = min(all_x)
        if self.y_max is None or self.y_max < max(all_y):
            self.y_max = max(all_y)
        if self.y_min is None or self.y_min > min(all_y):
            self.y_min = min(all_y)

    def fit_models(self):
        """Fit regression models for all lines in the graph.

        Iterates through the line models and fits their polynomial regressions.

        Returns:
            None
        """
        for key, item in self.dict_line.items():
            try:
                item.fit_regression()
            except ValueError as e:
                print(f"Error fitting regression for {key}: {e}")

    def clear_train_data(self):
        """Clear training data for all line models.

        Resets training data in each Line instance to free memory.

        Returns:
            None
        """
        for key, item in self.dict_line.items():
            try:
                item.clear_train_data()
            except ValueError as e:
                print(f"Error fitting regression for {key}: {e}")

    def save_graph(self):
        """Save the graph metadata and line models to disk.

        Serializes the graph metadata to a JSON file and saves each Line model polynomial
        features and regression to pickle files.

        Returns:
            None
        """
        info_graph = {
            "name": self.name,
            "dict_line": {},
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
        }

        dict_lines = {}
        for key, item in self.dict_line.items():
            line = {
                "type_line": item.type_line.value,
                "polynomial_features": f"{item.type_line.value}_polynomial_features.pkl",
                "polynomial_regression": f"{item.type_line.value}_polynomial_regression.pkl",
            }

            path_graph = Paths.MODEL_DIRECTORY / f"{self.name}"
            if not path_graph.exists():
                path_graph.mkdir()

            joblib.dump(item.polynomial_features, path_graph / line["polynomial_features"])
            joblib.dump(item.polynomial_regression, path_graph / line["polynomial_regression"])

            dict_lines[key.value] = line

        info_graph["dict_line"] = dict_lines

        json_path = Paths.MODEL_DIRECTORY / f"{self.name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(info_graph, f, indent=4, ensure_ascii=False)

    def load_graph(self) -> None:
        """Load the graph metadata and line models from disk.

        Reads metadata from a JSON file and restores Line models from pickle files.

        Returns:
            None

        Raises:
            Exception: If the JSON file does not exist.
            ValueError: If the JSON data is invalid or the graph name mismatches.
        """
        json_path = Paths.MODEL_DIRECTORY / f"{self.name}.json"
        if json_path.exists():
            with open(json_path, encoding="utf-8") as f:
                info_graph = json.load(f)
        else:
            raise Exception("File not exist")

        if info_graph is None or not isinstance(info_graph, dict):
            raise ValueError("File is not JSON")
        else:
            info_graph = dict(info_graph)

        if self.name != info_graph["name"]:
            raise ValueError("Error loading graph data")

        self.name = info_graph["name"]
        self.area = info_graph["area"]
        self.code_area = info_graph["code_area"]
        self.breed = info_graph["breed"]
        self.code_breed = info_graph["code_breed"]
        self.condition = info_graph["condition"]
        self.code_condition = info_graph["code_condition"]
        self.age_thinning = float(info_graph["age_thinning"])
        self.age_thinning_save = float(info_graph["age_thinning_save"])
        self.x_max = float(info_graph["x_max"])
        self.x_min = float(info_graph["x_min"])
        self.y_max = float(info_graph["y_max"])
        self.y_min = float(info_graph["y_min"])
        self.x_min_economic = float(info_graph["x_min_economic"])

        dict_lines = dict(info_graph["dict_line"])
        for key, line in dict_lines.items():
            type_line = TypeLine.give_enum_from_value(line["type_line"])
            polynomial_features = joblib.load(Paths.MODEL_DIRECTORY / self.name / line["polynomial_features"])
            polynomial_regression = joblib.load(Paths.MODEL_DIRECTORY / self.name / line["polynomial_regression"])

            item = Line(
                type_line=type_line,
                polynomial_features=polynomial_features,
                polynomial_regression=polynomial_regression,
            )

            self.dict_line[type_line] = item

    def predict_value(self, type_line: TypeLine, X: float, start_parameter: float = 0) -> float:
        """Predict a single y-value for a given line type and x-value.

        Validates the line type and start parameter, then computes the prediction using
        the corresponding Line model.

        Args:
            type_line (TypeLine): The type of line to predict (e.g., growth, logging).
            X (float): The x-value for prediction.
            start_parameter (float, optional): Starting parameter, must be 0 for non-growth/recovery lines.
            Defaults to 0.

        Returns:
            float: The predicted y-value.

        Raises:
            ValueError: If the line type is not found or start_parameter is invalid.
        """
        if type_line not in self.dict_line:
            raise ValueError(f"Type line {type_line} not found")
        if type_line != TypeLine.GROWTH_LINE and type_line != TypeLine.RECOVERY_LINE and start_parameter != 0:
            text = f"Value {start_parameter} of starting parameter is unacceptable for {type_line} type of line."
            raise ValueError(text)

        model_line = self.dict_line[type_line]
        result = model_line.predict_value(X, start_parameter)
        return result

    def predict_list_value(self, type_line: TypeLine, X: list[float], start_parameter: float = 0) -> list[float]:
        """Predict y-values for a list of x-values and a line type.

        Validates the line type and start parameter, then computes predictions using
        the corresponding Line model.

        Args:
            type_line (TypeLine): The type of line to predict (e.g., growth, logging).
            X (list[float]): List of x-values for prediction.
            start_parameter (float, optional): Starting parameter, must be 0 for non-growth/recovery lines.
            Defaults to 0.

        Returns:
            list[float]: List of predicted y-values.

        Raises:
            ValueError: If the line type is not found or start_parameter is invalid.
        """
        if type_line not in self.dict_line:
            raise ValueError(f"Type line {type_line} not found")
        if type_line != TypeLine.GROWTH_LINE and type_line != TypeLine.RECOVERY_LINE and start_parameter != 0:
            text = f"Value {start_parameter} of starting parameter is unacceptable for {type_line} type of line."
            raise ValueError(text)

        model_line = self.dict_line[type_line]
        result = model_line.predict_list_value(X, start_parameter)
        return result

    def predict_line(
        self,
        type_line: TypeLine,
        start_x: float = None,
        end_x: float = None,
        step: float = None,
        start_parameter: float = 0,
    ) -> list[float]:
        """Generate x and y values for a line type over a range.

        Validates the line type and start parameter, adjusts ranges for economic lines,
        and computes predictions using the corresponding Line model.

        Args:
            type_line (TypeLine): The type of line to predict (e.g., growth, logging).
            start_x (float, optional): Starting x-value. Defaults to x_min or x_min_economic for economic lines.
            end_x (float, optional): Ending x-value. Defaults to x_max.
            step (float, optional): Step size between x-values. Defaults to Settings.STEP_PLOTTING_GRAPH.
            start_parameter (float, optional): Starting parameter, must be 0 for non-growth/recovery lines.
                Defaults to 0.

        Returns:
            tuple[list[float], list[float]]: A tuple of (x_values, y_values) for the predicted line.

        Raises:
            ValueError: If the line type is not found or start_parameter is invalid.
            Exception: If start_x is not less than end_x.
        """
        if type_line != TypeLine.GROWTH_LINE and type_line != TypeLine.RECOVERY_LINE and start_parameter != 0:
            text = f"Value {start_parameter} of starting parameter is unacceptable for {type_line} type of line."
            raise ValueError(text)
        if start_x < end_x:
            raise Exception(f"Incorrect value start_x: {start_x} and end_x: {end_x}")
        if type_line not in self.dict_line:
            raise ValueError(f"Type line {type_line} not found")

        if type_line == TypeLine.ECONOMIC_MIN_LINE:
            start_x = self.x_min_economic

        if start_x is None:
            start_x = self.x_min
        if end_x is None:
            end_x = self.x_max
        if step is None:
            step = Settings.STEP_PLOTTING_GRAPH

        model_line = self.dict_line[type_line]
        result_x, result_y = model_line.predict_line(
            start_x=start_x, end_x=end_x, step=step, start_point=start_parameter
        )
        return result_x, result_y

    def get_list_record_planned_thinning(self) -> list[dict[str, float]]:
        """Retrieve the list of planned thinning events.

        Returns the recorded thinning events from the simulation, each containing the date,
        value before thinning, and value after thinning.

        Returns:
            list[dict[str, float]]: A list of dictionaries with 'x', 'past_value', and 'new_value' keys
                for thinning events.

        Raises:
            ValueError: If the thinning events list is not initialized.
        """
        return self.list_record_planned_thinning

    def get_list_value_track_thinning(self) -> dict[str, list[float]]:
        """Retrieve the growth track with thinning events.

        Returns the x and y values representing the forest growth trajectory, accounting for
        thinning events.

        Returns:
            dict[str, list[float]]: A dictionary with 'x' and 'y' keys containing lists of
                x-values and y-values for the growth track.

        Raises:
            ValueError: If the growth track is not initialized.
        """
        return self.list_value_track_thinning

    def add_thinning(self, date_thinning: float) -> None:
        """Add a thinning event at the specified date.

        Inserts a new thinning event at the given date, calculating the value before and after
        thinning based on the growth or recovery line, and updates the thinning simulation from
        that point.

        Args:
            date_thinning (float): The date (x-value) for the thinning event.

        Returns:
            None

        Raises:
            ValueError: If the thinning events list is not initialized or date_thinning is invalid.
        """
        if self.list_record_planned_thinning is None:
            self.list_record_planned_thinning = []
        list_record_planned_thinning = self.list_record_planned_thinning

        index = 0
        for i in range(len(list_record_planned_thinning)):
            if list_record_planned_thinning[i]["x"] <= date_thinning:
                index = i
            else:
                break

        if index > 0:
            start_parameter = list_record_planned_thinning[index]["x"]
            old_value = self.predict_value(
                type_line=TypeLine.RECOVERY_LINE, X=date_thinning, start_parameter=start_parameter
            )
        else:
            start_parameter = 0
            old_value = None
            for i in range(len(self.list_value_x)):
                if self.list_value_x[i] <= date_thinning:
                    old_value = self.bearing_value_y_line[i]
        new_value = None
        for i in range(len(self.list_value_x)):
            if self.list_value_x[i] <= date_thinning:
                new_value = self.list_value_y_min_logging[i]

        list_record_planned_thinning = list_record_planned_thinning[: index + 1]
        list_record_planned_thinning.append(
            {
                "x": date_thinning,
                "past_value": old_value,
                "new_value": new_value,
            }
        )

        from_end_simulation = self.simulation_thinning(start_date=date_thinning)
        list_record_planned_thinning.extend(from_end_simulation)

        self.list_record_planned_thinning = list_record_planned_thinning

        self.initialize_track_thinning()

    def correct_thinning(self, date_thinning: float, value_thinning: float) -> None:
        """Correct the value of a thinning event at the specified date.

        Updates the thinning event at the given date with a new value, recalculates the
        starting parameter for the recovery line, and updates the simulation from that point.

        Args:
            date_thinning (float): The date (x-value) of the thinning event to correct.
            value_thinning (float): The new value after thinning.

        Returns:
            None

        Raises:
            ValueError: If the thinning events list is not initialized or date_thinning is invalid.
        """
        list_record_planned_thinning = self.list_record_planned_thinning
        list_value_x = [x for x in self.list_value_x if x < date_thinning]
        different_past = value_thinning
        start_parameter = 0
        for current_index in range(len(list_value_x) - 1, -1, -1):
            predict_value = self.predict_value(
                type_line=TypeLine.RECOVERY_LINE, X=date_thinning, start_parameter=list_value_x[current_index]
            )
            different = abs(predict_value - value_thinning)
            if different < different_past:
                different_past = different
                start_parameter = list_value_x[current_index]
            else:
                break

        index = 0
        for i in range(len(list_record_planned_thinning)):
            if list_record_planned_thinning[i]["x"] < date_thinning:
                continue
            else:
                index = i
                break

        list_record_planned_thinning = list_record_planned_thinning[: index + 1]
        list_record_planned_thinning[-1] = {
            "x": list_record_planned_thinning[-1].get("x"),
            "past_value": list_record_planned_thinning[-1].get("past_value"),
            "new_value": value_thinning,
        }

        from_end_simulation = self.simulation_thinning(start_date=date_thinning, parameter_predict=start_parameter)

        list_record_planned_thinning.extend(from_end_simulation)

        self.list_record_planned_thinning = list_record_planned_thinning

        self.initialize_track_thinning()

    def delete_thinning(self, index: int) -> None:
        """Delete a thinning event at the specified index and update the growth track.

        Removes the thinning event at the given index, recalculates the subsequent event’s
        values using the growth or recovery line based on prior events, and reinitializes
        the growth track.

        Args:
            index (int): The index of the thinning event to delete.

        Returns:
            None

        Raises:
            IndexError: If the index is out of range for the thinning events list.
        """
        list_record_planned_thinning = self.list_record_planned_thinning

        if index > 0:
            past_element = list_record_planned_thinning[index - 1]
            start_parameter = past_element["x"]
        else:
            start_parameter = self.bearing_value_parameter
        next_element = list_record_planned_thinning[index + 1]
        new_value = next_element["new_value"]
        new_x = next_element["x"]

        if index == 0:
            next_value = self.predict_value(type_line=TypeLine.GROWTH_LINE, X=new_x, start_parameter=start_parameter)
        else:
            next_value = self.predict_value(type_line=TypeLine.RECOVERY_LINE, X=new_x, start_parameter=start_parameter)

        del list_record_planned_thinning[index]

        list_record_planned_thinning[index] = {
            "x": new_x,
            "past_value": next_value,
            "new_value": new_value,
        }

        self.list_record_planned_thinning = list_record_planned_thinning
        self.initialize_track_thinning()

    def check_graph_save_forest(self):
        """Check and adjust thinning events based on protective forest mode.

        Removes thinning events that occur after the thinning age limit (determined by
        flag_save_forest) and reinitializes the growth track. Uses age_thinning_save for
        protective forests or age_thinning otherwise.

        Returns:
            None

        Raises:
            IndexError: If the thinning events list is empty or has fewer than two events.
        """
        list_record_planned_thinning = self.list_record_planned_thinning
        if self.flag_save_forest:
            age_cancel_thinning = self.age_thinning_save
        else:
            age_cancel_thinning = self.age_thinning
        while True:
            if list_record_planned_thinning[-2].get("x") > age_cancel_thinning:
                del list_record_planned_thinning[-2]
            if list_record_planned_thinning[-2].get("x") < age_cancel_thinning:
                break
        self.list_record_planned_thinning = list_record_planned_thinning
        self.initialize_track_thinning()

    def simulation_thinning(
        self, start_date: float = None, parameter_predict: float = None
    ) -> tuple[dict[str, list[float]], list[dict[str, float]]]:
        """Simulate forest thinning based on growth and logging lines.

        Tracks forest growth along the bearing line, triggers thinning when the value
        exceeds the economic minimum and bearing line, and switches to the recovery line
        post-thinning. Records thinning events starting from start_date if provided, adding
        a final event with a near-zero value at the end of the simulation range.

        Args:
            start_date (float, optional): The starting date for the simulation. If None,
                starts from the beginning. Defaults to None.
            parameter_predict (float, optional): The starting parameter for recovery line
                predictions if start_date is provided. Defaults to None.

        Returns:
            list[dict[str, float]]: A list of dictionaries with 'x', 'past_value', and
                'new_value' keys for thinning events, including a final event with a near-zero
                value (0.000000000001).

        Raises:
            ValueError: If required lines (bearing, logging, economic) or x-values are not initialized.
        """
        if start_date is not None:
            list_value_x = [x for x in self.list_value_x if x >= start_date]
            bearing_value_y_line = self.bearing_value_y_line[len(self.list_value_x) - len(list_value_x) :]
            list_value_y_min_economic = self.list_value_y_min_economic[len(self.list_value_x) - len(list_value_x) :]
            list_value_y_min_logging = self.list_value_y_min_logging[len(self.list_value_x) - len(list_value_x) :]
        else:
            list_value_x = self.list_value_x
            bearing_value_y_line = self.bearing_value_y_line
            list_value_y_min_economic = self.list_value_y_min_economic
            list_value_y_min_logging = self.list_value_y_min_logging
        list_value_x = [x for x in list_value_x if x <= self.age_thinning]

        if self.flag_save_forest:
            cutting_limit = self.age_thinning_save
        else:
            cutting_limit = self.age_thinning
        list_record_planned_thinning = []

        if start_date is None:
            start_parameter = self.bearing_value_parameter
            current_value = self.bearing_value_parameter
            flag_thinning = False
        else:
            flag_thinning = True
            current_value = None
            if parameter_predict is not None:
                start_parameter = parameter_predict
            else:
                start_parameter = list_value_x[0]

        for current_index in range(len(list_value_x)):
            if not flag_thinning:
                current_value = self.bearing_value_y_line[current_index]
            else:
                current_value = self.predict_value(
                    type_line=TypeLine.RECOVERY_LINE,
                    X=list_value_x[current_index],
                    start_parameter=start_parameter,
                )
                if current_value < self.list_value_y_min_logging[current_index]:
                    current_value = self.list_value_y_min_logging[current_index]

            if (
                current_value >= bearing_value_y_line[current_index]
                and list_value_x[current_index] > self.x_min_economic
                and current_value >= list_value_y_min_economic[current_index]
                and list_value_x[current_index] <= cutting_limit
            ):
                past_value = current_value
                new_value = list_value_y_min_logging[current_index]
                list_record_planned_thinning.append(
                    {
                        "x": list_value_x[current_index],
                        "past_value": past_value,
                        "new_value": new_value,
                    }
                )
                flag_thinning = True
                current_value = new_value
                start_parameter = list_value_x[current_index]

        if not flag_thinning:
            current_value = self.bearing_value_y_line[-1]
        else:
            current_value = self.predict_value(
                type_line=TypeLine.RECOVERY_LINE,
                X=list_value_x[-1],
                start_parameter=start_parameter,
            )
            if current_value < self.list_value_y_min_logging[-1]:
                current_value = self.list_value_y_min_logging[-1]
        list_record_planned_thinning.append(
            {
                "x": self.list_value_x[-1],
                "past_value": current_value,
                "new_value": 0.000000000001,
            }
        )

        if self.list_record_planned_thinning is None:
            self.list_record_planned_thinning = list_record_planned_thinning

        return list_record_planned_thinning

    def initialize_track_thinning(self) -> None:
        """Initialize the growth track with thinning events.

        Generates x and y values for the forest growth trajectory, incorporating thinning
        events from list_record_planned_thinning, using growth and recovery lines. Stores
        the result in list_value_track_thinning.

        Returns:
            None

        Raises:
            Exception: If list_record_planned_thinning is not initialized.
        """
        if self.list_record_planned_thinning is None:
            raise Exception("list_record_planned_thinning is None")

        result_track_x: list[float] = []
        result_track_y: list[float] = []
        start_parameter = self.bearing_value_parameter
        current_value = self.bearing_value_parameter
        flag_thinning = False
        number_thinning = 0
        for current_index in range(len(self.list_value_x)):
            if not flag_thinning:
                current_value = self.bearing_value_y_line[current_index]
            else:
                current_value = self.predict_value(
                    type_line=TypeLine.RECOVERY_LINE,
                    X=self.list_value_x[current_index],
                    start_parameter=start_parameter,
                )
                if current_value < self.list_value_y_min_logging[current_index]:
                    current_value = self.list_value_y_min_logging[current_index]

            result_track_x.append(self.list_value_x[current_index])
            result_track_y.append(current_value)

            if self.list_value_x[current_index] >= self.list_record_planned_thinning[number_thinning]["x"]:
                flag_thinning = True
                past_value = self.list_record_planned_thinning[number_thinning]["past_value"]
                new_value = self.list_record_planned_thinning[number_thinning]["new_value"]
                current_value = new_value

                number_thinning += 1
                # if new_value == self.list_value_y_min_logging[current_index]:
                #     start_parameter = self.list_value_x[current_index]
                # else:
                if number_thinning < len(self.list_record_planned_thinning):
                    true_value_next = self.list_record_planned_thinning[number_thinning]["past_value"]
                    date_next = self.list_record_planned_thinning[number_thinning]["x"]
                    different_past = true_value_next
                    for j in range(current_index, -1, -1):
                        predict_value = self.predict_value(
                            type_line=TypeLine.RECOVERY_LINE, X=date_next, start_parameter=self.list_value_x[j]
                        )
                        different = abs(predict_value - true_value_next)
                        if different < different_past:
                            different_past = different
                            start_parameter = self.list_value_x[j]
                        else:
                            break

                # Для y координаты - создаем последовательность от начального до конечного значения
                y_cut = np.arange(start=past_value, stop=new_value, step=-1 * Settings.STEP_VALUE_GRAPH)
                # Для x координаты - повторяем текущий возраст нужное количество раз
                x_cut = np.full_like(y_cut, self.list_value_x[current_index])

                # Добавляем точки в общий график
                result_track_x.extend(x_cut)
                result_track_y.extend(y_cut)
        self.list_value_track_thinning = {
            "x": result_track_x,
            "y": result_track_y,
        }
        return self.list_value_track_thinning

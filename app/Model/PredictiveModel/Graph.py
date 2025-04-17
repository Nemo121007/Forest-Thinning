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
        y_min_economic (float): Minimum x-value for the economic minimum line.
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
        self.y_min_economic: float = None
        self.list_value_x: list[float] = None

        self.step: float = Settings.STEP_PLOTTING_GRAPH
        self.list_value_y_min_logging: list[float] = None
        self.list_value_y_max_logging: list[float] = None
        self.list_value_y_min_economic: list[float] = None

        self.bearing_value_parameter: float = None
        self.bearing_value_y_line: list[float] = None

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
        self.y_min_economic: float = None

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

        self.list_value_x = np.arange(self.x_min, self.x_max + step, step).tolist()
        self.list_value_y_min_logging = self.predict_list_value(
            type_line=TypeLine.MIN_LEVEL_LOGGING, X=self.list_value_x, start_parameter=0
        )
        self.list_value_y_max_logging = self.predict_list_value(
            type_line=TypeLine.MAX_LEVEL_LOGGING, X=self.list_value_x, start_parameter=0
        )
        self.list_value_y_min_economic = self.predict_list_value(
            type_line=TypeLine.ECONOMIC_MIN_LINE, X=self.list_value_x, start_parameter=0
        )

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

    def get_base_lines_graph(self) -> tuple[list[float], list[float], list[float], list[float]]:
        """Retrieve the x-values and y-values for base lines (logging and economic minimum).

        Returns the x-values and predicted y-values for minimum logging, maximum logging,
        and economic minimum lines.

        Returns:
            tuple[list[float], list[float], list[float], list[float]]: A tuple containing:
                - List of x-values.
                - List of y-values for minimum logging line.
                - List of y-values for maximum logging line.
                - List of y-values for economic minimum line.

        Raises:
            ValueError: If the base lines have not been initialized.
        """
        return (
            self.list_value_x,
            self.list_value_y_min_logging,
            self.list_value_y_max_logging,
            self.list_value_y_min_economic,
        )

    def set_bearing_parameter(self, bearing_parameter: float = None) -> None:
        """Set the bearing parameter for the growth line.

        Assigns the bearing parameter either as the provided value or as the average of
        the minimum and maximum logging lines’ initial y-values if none is provided.

        Args:
            bearing_parameter (float, optional): The bearing parameter value. Defaults to None.

        Returns:
            None

        Raises:
            ValueError: If the logging lines’ y-values are not initialized.
        """
        if bearing_parameter is None:
            self.bearing_value_parameter = (self.list_value_y_min_logging[0] + self.list_value_y_max_logging[0]) / 2
        else:
            self.bearing_value_parameter = bearing_parameter

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
                if self.y_min_economic is None or self.y_min_economic > min(all_x):
                    self.y_min_economic = min(all_x)
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
            "y_min_economic": self.y_min_economic,
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
        self.y_min_economic = float(info_graph["y_min_economic"])

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
            start_x (float, optional): Starting x-value. Defaults to x_min or y_min_economic for economic lines.
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
            start_x = self.y_min_economic

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

    def simulation_thinning(self) -> tuple[dict[str, list[float]], list[dict[str, float]]]:
        """Simulate forest thinning based on growth and logging lines.

        Tracks the forest’s growth along the bearing line, triggers thinning when the value
        exceeds the economic minimum and bearing line, and switches to the recovery line
        post-thinning. Records the growth track and thinning events.

        Returns:
            tuple[dict[str, list[float]], list[dict[str, float]]]: A tuple containing:
                - dict of list with 'x' and 'y' keys for the growth track.
                - List of dictionaries with 'x', 'past_value', and 'new_value' keys for thinning events.

        Raises:
            ValueError: If required lines (bearing, logging, economic) or x-values are not initialized.
        """
        if self.flag_save_forest:
            list_value_x = [x for x in self.list_value_x if x <= self.age_thinning_save]
        else:
            list_value_x = [x for x in self.list_value_x if x <= self.age_thinning]
        result_track_x: list[float] = []
        result_track_y: list[float] = []
        list_record_planned_thinning = []
        start_parameter = self.bearing_value_parameter
        current_value = self.bearing_value_parameter
        flag_thinning = False
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

            result_track_x.append(list_value_x[current_index])
            result_track_y.append(current_value)

            if (
                current_value >= self.bearing_value_y_line[current_index]
                and current_value >= self.list_value_y_min_economic[current_index]
            ):
                flag_thinning = True
                start_parameter = list_value_x[current_index]
                list_record_planned_thinning.append(
                    {
                        "x": list_value_x[current_index],
                        "past_value": current_value,
                        "new_value": self.list_value_y_min_logging[current_index],
                    }
                )
                current_value = self.list_value_y_min_logging[current_index]
                result_track_x.append(list_value_x[current_index])
                result_track_y.append(current_value)
        list_record_planned_thinning.append(
            {
                "x": list_value_x[current_index],
                "past_value": current_value,
                "new_value": 0.000000000001,
            }
        )

        return (
            {
                "x": result_track_x,
                "y": result_track_y,
            },
            list_record_planned_thinning,
        )

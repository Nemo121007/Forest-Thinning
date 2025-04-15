"""Module for managing graph data and prediction models in a reference data system.

This module provides the Graph class, which handles graph data associated with areas, breeds,
and conditions, storing multiple line models (e.g., growth, logging) and supporting data loading,
model fitting, prediction, and serialization.
"""

import json
import tarfile
import joblib
from ...background_information.Paths import Paths

from .Line import Line
from ...background_information.Type_line import Type_line
from ...background_information.Settings import Settings


class Graph:
    """A class for managing graph data and associated prediction models.

    Stores graph metadata (area, breed, condition) and a collection of Line models for
    different line types (e.g., growth, logging). Supports loading data from tar files,
    fitting polynomial regression models, making predictions, and saving/loading model state.

    Attributes:
        name (str): The name of the graph (file name).
        dict_line (dict[Type_line, Line]): Dictionary mapping line types to Line models.
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
        self.dict_line: dict[Type_line, Line] = {}
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
        self.dict_line: dict[Type_line, Line] = {}
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
        name_line = Type_line.give_enum_from_value(value=line["name"])

        # Для построения графика достаточно MIN_LEVEL_LOGGING,
        # MAX_LEVEL_LOGGING, ECONOMIC_MIN_LINE, GROWTH_LINE и RECOVERY_LINE
        if (
            name_line == Type_line.MIN_LEVEL_LOGGING
            or name_line == Type_line.MAX_LEVEL_LOGGING
            or name_line == Type_line.ECONOMIC_MIN_LINE
        ):
            item.load_info(type_line=name_line)
            self.dict_line[name_line] = item
            if name_line == Type_line.ECONOMIC_MIN_LINE:
                if self.x_min_economic is None or self.x_min_economic > min(all_x):
                    self.x_min_economic = min(all_x)
        elif name_line == Type_line.GROWTH_LINE or name_line == Type_line.RECOVERY_LINE:
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

    def predict_value(self, type_line: Type_line, X: float, start_parameter: float = 0) -> float:
        """Predict a single y-value for a given line type and x-value.

        Validates the line type and start parameter, then computes the prediction using
        the corresponding Line model.

        Args:
            type_line (Type_line): The type of line to predict (e.g., growth, logging).
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
        if type_line != Type_line.GROWTH_LINE and type_line != Type_line.RECOVERY_LINE and start_parameter != 0:
            text = f"Value {start_parameter} of starting parameter is unacceptable for {type_line} type of line."
            raise ValueError(text)

        model_line = self.dict_line[type_line]
        result = model_line.predict_value(X, start_parameter)
        return result

    def predict_list_value(self, type_line: Type_line, X: list[float], start_parameter: float = 0) -> list[float]:
        """Predict y-values for a list of x-values and a line type.

        Validates the line type and start parameter, then computes predictions using
        the corresponding Line model.

        Args:
            type_line (Type_line): The type of line to predict (e.g., growth, logging).
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
        if type_line != Type_line.GROWTH_LINE and type_line != Type_line.RECOVERY_LINE and start_parameter != 0:
            text = f"Value {start_parameter} of starting parameter is unacceptable for {type_line} type of line."
            raise ValueError(text)

        model_line = self.dict_line[type_line]
        result = model_line.predict_list_value(X, start_parameter)
        return result

    def predict_line(
        self,
        type_line: Type_line,
        start_x: float = None,
        end_x: float = None,
        step: float = None,
        start_parameter: float = 0,
    ) -> list[float]:
        """Generate x and y values for a line type over a range.

        Validates the line type and start parameter, adjusts ranges for economic lines,
        and computes predictions using the corresponding Line model.

        Args:
            type_line (Type_line): The type of line to predict (e.g., growth, logging).
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
        if type_line != Type_line.GROWTH_LINE and type_line != Type_line.RECOVERY_LINE and start_parameter != 0:
            text = f"Value {start_parameter} of starting parameter is unacceptable for {type_line} type of line."
            raise ValueError(text)
        if start_x < end_x:
            raise Exception(f"Incorrect value start_x: {start_x} and end_x: {end_x}")
        if type_line not in self.dict_line:
            raise ValueError(f"Type line {type_line} not found")

        if type_line == Type_line.ECONOMIC_MIN_LINE:
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
            type_line = Type_line.give_enum_from_value(line["type_line"])
            polynomial_features = joblib.load(Paths.MODEL_DIRECTORY / self.name / line["polynomial_features"])
            polynomial_regression = joblib.load(Paths.MODEL_DIRECTORY / self.name / line["polynomial_regression"])

            item = Line(
                type_line=type_line,
                polynomial_features=polynomial_features,
                polynomial_regression=polynomial_regression,
            )

            self.dict_line[type_line] = item


if __name__ == "__main__":
    a = Graph("pine_sorrel")
    a.load_graph_from_tar()
    # a.load_graph_in_tar('nortTaiga_pine_lingonberry')
    a.fit_models()
    a.load_graph_from_tar(test_mark=True)
    a.check_graph()

    print("Check save graph")
    a.save_graph()
    a = Graph("pine_sorrel")
    a.load_graph()
    a.load_graph_from_tar(test_mark=True)
    a.check_graph()
    print(a)

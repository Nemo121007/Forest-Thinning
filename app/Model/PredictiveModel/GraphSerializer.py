"""Module for serializing and deserializing graph data in forest growth simulations.

This module defines the GraphSerializer class, which handles loading and saving graph data,
including metadata (via GraphData) and line models (via LineManager). It supports loading
from tar archives and saving/loading to JSON and pickle files for forest growth and thinning
simulations.

Dependencies:
    - json: Standard library module for JSON serialization.
    - tarfile: Standard library module for handling tar archives.
    - joblib: Library for serializing machine learning models.
    - GraphData: Dataclass for storing graph metadata.
    - LineManager: Class for managing Line objects.
    - Line: Class representing a single line model.
    - TypeLine: Enum defining types of lines (e.g., GROWTH_LINE, RECOVERY_LINE).
    - Paths: Class defining file paths for data and model storage.
"""

import json
from pathlib import Path
import tarfile
import joblib
from ...background_information.Paths import Paths
from .Line import Line
from ...background_information.TypeLine import TypeLine
from .GraphData import GraphData
from .LineManager import LineManager


class GraphSerializer:
    """Serializer for loading and saving graph data in forest growth simulations.

    Manages serialization and deserialization of graph metadata (via GraphData) and line
    models (via LineManager). Supports loading graph data from tar archives and saving/loading
    to JSON and pickle files, including polynomial regression models for lines.

    Attributes:
        graph_data (GraphData): The metadata of the graph, including area, breed, and min/max values.
        line_manager (LineManager): The manager for Line objects associated with TypeLine enums.
    """

    def __init__(self, graph_data: GraphData, line_manager: LineManager):
        """Initialize the GraphSerializer with graph metadata and line manager.

        Sets up the serializer with the provided GraphData and LineManager instances for
        handling graph serialization and deserialization.

        Args:
            graph_data (GraphData): The metadata of the graph to serialize.
            line_manager (LineManager): The manager for Line objects to serialize.

        Returns:
            None
        """
        self.graph_data = graph_data
        self.line_manager = line_manager

    def load_graph_from_tar(self) -> None:
        """Load graph data from a tar archive.

        Reads graph data from a tar archive located in the data directory, expecting a JSON
        file (wpd.json) in a folder named after the graph. Updates graph_data and line_manager
        with loaded data, including x and y values for supported line types.

        Returns:
            None

        Raises:
            FileNotFoundError: If the tar file does not exist in the data directory.
            ValueError: If the JSON data is invalid or missing the 'datasetColl' key.
            tarfile.TarError: If there is an error reading the tar archive.
            json.JSONDecodeError: If the JSON file cannot be decoded.
        """
        tar_path = Paths.DATA_DIRECTORY / f"{self.graph_data.name}.tar"
        if not tar_path.exists():
            raise FileNotFoundError(f"Tar file {tar_path} does not exist")

        try:
            with tarfile.open(tar_path, "r") as tar:
                file_member = tar.getmember(f"{self.graph_data.name}/wpd.json")
                with tar.extractfile(file_member) as file:
                    data = json.load(file)
            if "datasetColl" not in data:
                raise ValueError("Key 'datasetColl' is missing in JSON data")

            for line_data in sorted(data["datasetColl"], key=lambda x: x["name"]):
                self._load_data_line_one_line(line_data)
        except (tarfile.TarError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to load graph from tar: {e}")

    def _extract_line_data(self, line_data: dict) -> tuple[list[float], list[float]]:
        """Extract x and y values from line data.

        Processes a dictionary containing line data, extracting x and y values from the 'data'
        field, where each item is expected to have a 'value' key with a list of [x, y].

        Args:
            line_data (dict): A dictionary with a 'data' key containing a list of dictionaries,
                each with a 'value' key holding [x, y] pairs.

        Returns:
            tuple[list[float], list[float]]: A tuple of (x_values, y_values) lists.

        Raises:
            ValueError: If the number of x and y values does not match or if the data is malformed.
        """
        x_values = [item["value"][0] for item in line_data["data"]]
        y_values = [item["value"][1] for item in line_data["data"]]
        if len(x_values) != len(y_values):
            raise ValueError("Number of x and y values does not match")
        return x_values, y_values

    def _update_line(self, line_type: TypeLine, x_values: list[float], y_values: list[float]) -> None:
        """Update or create a Line object in the LineManager.

        Updates an existing Line object or creates a new one for the specified TypeLine,
        appending the provided x and y values to its data.

        Args:
            line_type (TypeLine): The type of line to update or create.
            x_values (list[float]): The x-coordinates to append.
            y_values (list[float]): The y-coordinates to append.

        Returns:
            None
        """
        if line_type in self.line_manager.lines:
            line = self.line_manager.lines[line_type]
        else:
            line = Line()
            line.load_info(type_line=line_type)
            self.line_manager.add_line(type_line=line_type, line=line)
        line.append_data(X=x_values, Y=y_values)

    def _update_graph_data_bounds(self, line_type: TypeLine, x_values: list[float], y_values: list[float]) -> None:
        """Update the min/max bounds in GraphData based on line data.

        Updates x_min, x_max, y_min, y_max, and x_min_economic in graph_data based on the
        provided x and y values. For ECONOMIC_MIN_LINE, updates x_min_economic.

        Args:
            line_type (TypeLine): The type of line being processed.
            x_values (list[float]): The x-coordinates to consider.
            y_values (list[float]): The y-coordinates to consider.

        Returns:
            None
        """
        self.graph_data.x_max = (
            max(x_values) if self.graph_data.x_max is None else max(self.graph_data.x_max, max(x_values))
        )
        self.graph_data.x_min = (
            min(x_values) if self.graph_data.x_min is None else min(self.graph_data.x_min, min(x_values))
        )
        self.graph_data.y_max = (
            max(y_values) if self.graph_data.y_max is None else max(self.graph_data.y_max, max(y_values))
        )
        self.graph_data.y_min = (
            min(y_values) if self.graph_data.y_min is None else min(self.graph_data.y_min, min(y_values))
        )
        if line_type == TypeLine.ECONOMIC_MIN_LINE:
            self.graph_data.x_min_economic = (
                min(x_values)
                if self.graph_data.x_min_economic is None
                else min(self.graph_data.x_min_economic, min(x_values))
            )

    def _load_data_line_one_line(self, line_data: dict) -> None:
        """Process data for a single line from JSON data.

        Extracts the line type from the 'name' field, processes x and y values, and updates
        the line_manager and graph_data bounds. Ignores unsupported line types.

        Args:
            line_data (dict): A dictionary containing line data with 'name' and 'data' keys.

        Returns:
            None
        """
        line_type = TypeLine.give_enum_from_value(line_data["name"])
        if line_type not in (
            TypeLine.MIN_LEVEL_LOGGING,
            TypeLine.MAX_LEVEL_LOGGING,
            TypeLine.ECONOMIC_MIN_LINE,
            TypeLine.GROWTH_LINE,
            TypeLine.RECOVERY_LINE,
        ):
            return

        x_values, y_values = self._extract_line_data(line_data)
        self._update_line(line_type, x_values, y_values)
        self._update_graph_data_bounds(line_type, x_values, y_values)

    def _get_json_path(self) -> Path:
        """Generate the path to the JSON file for graph metadata.

        Returns the path to a JSON file in the model directory, named after the graph.

        Returns:
            Path: The path to the JSON file.
        """
        return Paths.MODEL_DIRECTORY / f"{self.graph_data.name}.json"

    def _get_model_path(self, filename: str) -> Path:
        """Generate the path to a model file in the model directory.

        Returns the path to a file in a subdirectory named after the graph within the model directory.

        Args:
            filename (str): The name of the model file (e.g., 'polynomial_features.pkl').

        Returns:
            Path: The path to the model file.
        """
        return Paths.MODEL_DIRECTORY / self.graph_data.name / filename

    def save_graph(self) -> None:
        """Save graph metadata and line models to JSON and pickle files.

        Serializes graph_data to a JSON file and line models (polynomial features and regression)
        to pickle files in a subdirectory named after the graph. Creates the model directory if
        it does not exist.

        Returns:
            None

        Raises:
            OSError: If there is an error creating directories or writing files.
        """
        info_graph = self.graph_data.to_dict()
        info_graph["dict_line"] = {}

        dict_lines = {}
        for type_line, line in self.line_manager.lines.items():
            line_info = {
                "type_line": type_line.value,
                "polynomial_features": f"{type_line.value} polynomial_features.pkl",
                "polynomial_regression": f"{type_line.value} polynomial_regression.pkl",
            }

            path_graph = Paths.MODEL_DIRECTORY / self.graph_data.name
            path_graph.mkdir(exist_ok=True)

            joblib.dump(line.polynomial_features, self._get_model_path(line_info["polynomial_features"]))
            joblib.dump(line.polynomial_regression, self._get_model_path(line_info["polynomial_regression"]))
            dict_lines[type_line.value] = line_info

        info_graph["dict_line"] = dict_lines
        with open(self._get_json_path(), "w", encoding="utf-8") as f:
            json.dump(info_graph, f, indent=4, ensure_ascii=False)

    def load_graph(self) -> None:
        """Load graph metadata and line models from JSON and pickle files.

        Reads graph metadata from a JSON file and line models from pickle files in a
        subdirectory named after the graph. Updates graph_data and line_manager with the
        loaded data, ensuring the graph name matches.

        Returns:
            None

        Raises:
            FileNotFoundError: If the JSON file or any model file does not exist.
            ValueError: If the JSON data is invalid or the graph name does not match.
        """
        json_path = self._get_json_path()
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file {json_path} does not exist")

        with open(json_path, encoding="utf-8") as f:
            info_graph = json.load(f)

        if not isinstance(info_graph, dict):
            raise ValueError("Invalid JSON data")
        if self.graph_data.name != info_graph["name"]:
            raise ValueError("Graph name mismatch")

        self.graph_data.from_dict(info_graph)

        for key, line_info in info_graph["dict_line"].items():
            type_line = TypeLine.give_enum_from_value(line_info["type_line"])
            polynomial_features = joblib.load(self._get_model_path(line_info["polynomial_features"]))
            polynomial_regression = joblib.load(self._get_model_path(line_info["polynomial_regression"]))
            line = Line(
                type_line=type_line,
                polynomial_features=polynomial_features,
                polynomial_regression=polynomial_regression,
            )
            self.line_manager.add_line(type_line, line)

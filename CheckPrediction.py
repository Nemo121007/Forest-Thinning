"""Module for managing and validating graph data with prediction models.

This module provides the Graph class, which handles graph data from tar files, stores
line models for prediction, and validates predictions against test data using visualization
and metrics.
"""

import json
import tarfile

from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score
from app.background_information.Paths import Paths

from app.Model.PredictiveModel.Line import Line
from app.background_information.TypeLine import TypeLine
from app.Model.PredictiveModel.Graph import Graph


class GraphCheck:
    """A class for managing graph data, predictions, and validation.

    Loads graph data from tar files, stores Line models for prediction, and supports
    validation by comparing predicted and test data with metrics (MSE, R2) and visualization.
    Tracks min/max ranges for x and y values.

    Attributes:
        name (str): The name of the graph (file name).
        file_name (Path): The path to the tar file containing graph data.
        dict_line (dict[TypeLine, Line]): Dictionary mapping line types to predicted Line models.
        dict_test (dict[TypeLine, Line]): Dictionary mapping line types to test Line models.
        x_max (float): Maximum x-value for the graph.
        x_min (float): Minimum x-value for the graph.
        y_max (float): Maximum y-value for the graph.
        y_min (float): Minimum y-value for the graph.
    """

    def __init__(self, name: str) -> None:
        """Initialize a Graph instance with a given name.

        Sets up the graph with a name, tar file path, and empty dictionaries for line models.

        Args:
            name (str): The name of the graph (used for file naming).

        Returns:
            None
        """
        self.name: str = name
        self.file_name = Paths.DATA_DIRECTORY / f"{name}.tar"
        self.dict_line: dict[TypeLine, Line] = {}
        self.dict_test: dict[TypeLine, Line] = {}
        self.x_max = None
        self.x_min = None
        self.y_max = None
        self.y_min = None

    def load_predicted_model(self, dict_line: dict[TypeLine, Line]) -> None:
        """Load predicted line models into the graph.

        Replaces the current dictionary of predicted line models with the provided one.

        Args:
            dict_line (dict[TypeLine, Line]): Dictionary mapping line types to Line models.

        Returns:
            None
        """
        self.dict_line = dict_line

    def load_data_test_from_tar(self):
        """Load test data from a tar file.

        Reads a JSON file from a tar archive, extracts line data, and populates test line
        models, updating min/max ranges.

        Returns:
            None

        Raises:
            Exception: If an error occurs while reading the tar file or parsing JSON data.
            KeyError: If the JSON data lacks the 'datasetColl' key.
        """
        tar_path = Paths.DATA_DIRECTORY / self.file_name

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
                    line = data_list[i]
                    self._load_data_line_one_line(line)

        except Exception as e:
            raise Exception(f"Error read data: {e}")

    def _load_data_line_one_line(self, line: dict) -> None:
        """Load test data for a single line from JSON data.

        Processes a line data, creates a Line model, and updates min/max ranges for test data.

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
        item.load_info(type_line=name_line)
        item.append_data(X=all_x, Y=all_y)
        self.dict_test[line["name"]] = item

        if self.x_max is None or self.x_max < max(all_x):
            self.x_max = max(all_x)
        if self.x_min is None or self.x_min > min(all_x):
            self.x_min = min(all_x)
        if self.y_max is None or self.y_max < max(all_y):
            self.y_max = max(all_y)
        if self.y_min is None or self.y_min > min(all_y):
            self.y_min = min(all_y)

    def predict(self, type_line: TypeLine, X: float, start_parameter: float = 0) -> float:
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

        model = self.dict_line[type_line]

        result = model.predict_value(X, start_parameter)

        return result

    def check_graph(self):
        """Validate predicted models against test data with visualization and metrics.

        Plots original and predicted lines, highlights significant deviations, and computes
        MSE and R2 scores for each line type. Prints the number of inflection points and
        maximum approximation error.

        Returns:
            None

        Raises:
            ValueError: If test data is missing.
        """
        if not self.dict_test:
            raise ValueError("Test data is missing")
        plt.figure(figsize=(15, 10))

        general_max_error = 0
        result_dict = {}
        for key, item in self.dict_test.items():
            max_different = 0
            name = TypeLine.give_enum_from_value(key)
            if name in [TypeLine.ECONOMIC_MAX_LINE, TypeLine.STANDARD_GROWTH_LINE]:
                continue
            plt.plot(item.X, item.Y, alpha=0.5, label=f"Original {key}", color="blue")

            list_args = []
            list_y = []
            list_predict = []
            list_predict_graph = graph.predict_list_value(
                type_line=item.type_line, x_values=item.X, start_parameter=item.start_parameter[0]
            )
            for i in range(len(item.X)):
                y_predict = list_predict_graph[i]

                if y_predict is None:
                    continue

                list_args.append(item.X[i])
                list_y.append(item.Y[i])
                list_predict.append(y_predict)
                different = item.Y[i] - y_predict

                # if different > 0 and symbol != "+" and abs(different) > 0.1:
                #     symbol = "+"
                #     list_change_symbol.append((item.X[i], different, symbol))
                #     plt.scatter(item.X[i], y_predict, color="red", label="Точки")
                # elif different < 0 and symbol != "-" and abs(different) > 0.1:
                #     symbol = "-"
                #     list_change_symbol.append((item.X[i], different, symbol))
                #     plt.scatter(item.X[i], y_predict, color="red", label="Точки")
                # if max_different < abs(different):
                #     max_different = abs(different)
                # if general_max_error < abs(different):
                #     general_max_error = abs(different)

            if result_dict.get(TypeLine.give_enum_from_value(key)):
                item = result_dict[TypeLine.give_enum_from_value(key)]
                item_true = list(item.get("true"))
                item_predict = list(item.get("predict"))
                item_true.extend(list_y)
                item_predict.extend(list_predict)
                result_dict[TypeLine.give_enum_from_value(key)] = {
                    "true": item_true,
                    "predict": item_predict,
                }
            else:
                item_true = []
                item_predict = []
                item_true.extend(list_y)
                item_predict.extend(list_predict)
                result_dict[TypeLine.give_enum_from_value(key)] = {
                    "true": item_true,
                    "predict": item_predict,
                }

            plt.plot(
                list_args,
                list_predict,
                label=f"Predicted {key}",
                linestyle="--",
                color="black",
            )
        general_max_error = 0
        for key, item in result_dict.items():
            max_different = 0
            list_y = item.get("true")
            list_predict = item.get("predict")
            mse_total = mean_squared_error(list_y, list_predict)
            r2_total = r2_score(list_y, list_predict)

            for i in range(len(list_y)):
                different = abs(list_y[i] - list_predict[i])
                if max_different < abs(different):
                    max_different = abs(different)
                if general_max_error < abs(different):
                    general_max_error = abs(different)

            # print(f"Количество перегибов {key}: {len(list_change_symbol)}")
            print(f"{key}: Количество измерений: {len(list_y)}")
            print(f"{key}: Общая MSE для обучающей выборки: {mse_total}")
            print(f"{key}: Общий R2 для обучающей выборки: {r2_total}")
            print(f"{key}: Максимальная ошибка при аппроксимации: {max_different}")

        print(f"Максимальная ошибка при аппроксимации: {general_max_error}")
        plt.title("Зависимость плотности лесов от времени\n График taiga_pine_sorrel")
        plt.xlabel("Время, года")
        plt.ylabel("Плотность, м²/га")
        plt.legend()
        plt.show()


if __name__ == "__main__":
    graph = Graph()
    graph.initialize_model(
        name="taiga_pine_sorrel",
        area="Area1",
        breed="Breed1",
        condition="Condition1",
        age_thinning=100.0,
        age_thinning_save=120.0,
        flag_save_forest=False,
    )
    graph.serializer.load_graph_from_tar()
    graph.line_manager.fit_models()

    print("Check save graph")
    test_graph = GraphCheck(name="taiga_pine_sorrel")
    test_graph.load_data_test_from_tar()
    test_graph.check_graph(save_graph=graph)

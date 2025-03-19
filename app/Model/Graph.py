"""Module for working with graphs."""

import json
import tarfile
import joblib

from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score
from app.background_information.Paths import Paths

from app.Model.Line import Line
from app.background_information.Type_line import Type_line


class Graph:
    """Class for working with graphs.

    Attributes:
        dict_line (dict[str, Line]): dictionary of lines
        dict_test (dict[str, Line]): dictionary of test lines

    Methods:
        load_graph_in_tar(name_file: str): Load graph data from a tar file
        _load_data_line(line: dict): Load data line
        fit_models(): Fit regression models for all lines
        check_graph(): Check the graph for the correctness of the approximation

    Raises:
        FileNotFoundError: File not found
        KeyError: Key error
        ValueError: Value error
    """

    def __init__(self, name: str) -> None:
        """Constructor.

        Args:
            name (str): name of the graph

        Returns:
            None
        """
        self.name: str = name
        self.file_name: str = f"{name}.tar"
        self.dict_line: dict[Type_line, Line] = {}
        self.dict_test: dict[Type_line, Line] = {}
        self.forest_area = None
        self.main_breed = None
        self.type_conditions = None
        self.flag_save_forest = False

    def set_data_graph(
        self,
        forest_area: str = None,
        main_breed: str = None,
        type_conditions: str = None,
        flag_save_forest: bool = None,
    ) -> None:
        """Set data about forest area, main breed, type conditions and status save forest graph.

        Args:
            forest_area (str): forest area
            main_breed (str): main breed
            type_conditions (str): type conditions
            flag_save_forest (bool): status save forest graph

        Returns:
            None
        """
        if forest_area is not None:
            self.forest_area = forest_area
        if main_breed is not None:
            self.main_breed = main_breed
        if type_conditions is not None:
            self.type_conditions = type_conditions
        if flag_save_forest is not None:
            self.flag_save_forest = flag_save_forest
        pass

    def load_graph_from_tar(self, test_mark: bool = False):
        """Load graph data from a tar file.

        Args:
            test_mark (bool): test mark

        Returns:
            None
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
                    self._load_data_line_one_line(line, test_mark)

        except FileNotFoundError:
            raise FileNotFoundError(f"File {tar_path} not found.")
        except KeyError as e:
            raise KeyError(f"Key error: {e}")
        except ValueError as e:
            raise ValueError(f"Value error: {e}")

    def _load_data_line_one_line(self, line: dict, test_mark: bool = False):
        all_x = []
        all_y = []

        # Извлечение данных для текущей линии
        for item in line["data"]:
            all_x.append(item["value"][0])
            all_y.append(item["value"][1])

        if len(all_x) != len(all_y):
            raise ValueError("The number of arguments X and Y does not match")

        item = Line()
        name_line = Type_line.give_enum_from_value(value=line["name"])
        if test_mark:
            if name_line == Type_line.GROWTH_LINE:
                item.load_data(
                    name=line["name"], type_line=Type_line.GROWTH_LINE, X=all_x, Y=all_y, start_parameter=all_y[0]
                )
            elif name_line == Type_line.RECOVERY_LINE:
                item.load_data(
                    name=line["name"], type_line=Type_line.RECOVERY_LINE, X=all_x, Y=all_y, start_parameter=all_x[0]
                )
            else:
                item.load_data(name=line["name"], type_line=name_line, X=all_x, Y=all_y, start_parameter=0)

            self.dict_test[line["name"]] = item
        else:
            if name_line == Type_line.GROWTH_LINE:
                if name_line in self.dict_line:
                    item = self.dict_line[name_line]
                    item.append_data(X=all_x, Y=all_y, start_parameter=all_y[0])
                else:
                    item.load_data(type_line=name_line, X=all_x, Y=all_y, start_parameter=all_y[0])
                    self.dict_line[name_line] = item
            elif name_line == Type_line.RECOVERY_LINE:
                if name_line in self.dict_line:
                    item = self.dict_line[name_line]
                    item.append_data(X=all_x, Y=all_y, start_parameter=all_x[0])
                else:
                    item.load_data(type_line=name_line, X=all_x, Y=all_y, start_parameter=all_x[0])
                    self.dict_line[name_line] = item
            else:
                item.load_data(type_line=name_line, X=all_x, Y=all_y, start_parameter=0)
                self.dict_line[name_line] = item

    def fit_models(self):
        """Fit regression models for all lines.

        Args:
            None

        Returns:
            None
        """
        for key, item in self.dict_line.items():
            try:
                item.fit_regression()
            except ValueError as e:
                print(f"Error fitting regression for {key}: {e}")

    def predict(self, type_line: Type_line, X: float, start_parameter: float = 0) -> float:
        """Predict the value of the function at the point X.

        Args:
            type_line (Type_line): type of line
            X (float): point X
            start_parameter (float): start parameter

        Returns:
            float: predicted value
        """
        if type_line not in self.dict_line:
            raise ValueError(f"Type line {type_line} not found")
        model = self.dict_line[type_line]
        return model.predict_value(X, start_parameter)

    def check_graph(self):
        """Check the graph for the correctness of the approximation.

        Args:
            None

        Returns:
            None
        """
        if not self.dict_test:
            raise ValueError("Test data is missing")
        plt.figure(figsize=(15, 10))

        max_different = 0
        for key, item in self.dict_test.items():
            plt.plot(item.X, item.Y, alpha=0.5, label=f"Original {key}", color="blue")

            symbol = ""
            list_change_symbol = []

            list_predict = []
            for i in range(len(item.X)):
                y_predict = self.predict(type_line=item.type_line, X=item.X[i], start_parameter=item.start_parameter[i])
                list_predict.append(y_predict)
                different = item.Y[i] - y_predict

                if different > 0 and symbol != "+" and abs(different) > 0.1:
                    symbol = "+"
                    list_change_symbol.append((item.X[i], different, symbol))
                    plt.scatter(item.X[i], y_predict, color="red", label="Точки")
                elif different < 0 and symbol != "-" and abs(different) > 0.1:
                    symbol = "-"
                    list_change_symbol.append((item.X[i], different, symbol))
                    plt.scatter(item.X[i], y_predict, color="red", label="Точки")
                if max_different < abs(different):
                    max_different = abs(different)

            plt.plot(
                item.X,
                list_predict,
                label=f"Predicted {key}",
                linestyle="--",
                color="black",
            )

            mse_total = mean_squared_error(item.Y, list_predict)
            r2_total = r2_score(item.Y, list_predict)

            print(f"Количество перегибов {item.name}: {len(list_change_symbol)}")
            print(f"{item.name}: Общая MSE для обучающей выборки: {mse_total}")
            print(f"{item.name}: Общий R2 для обучающей выборки: {r2_total}")

        print(f"Максимальная ошибка при аппроксимации: {max_different}")
        plt.show()

    def save_graph(self):
        """Save graph data to a tar file.

        Args:
            None

        Returns:
            None
        """
        info_graph = {
            "name": self.name,
            "file_name": self.file_name,
            "dict_line": {},
        }

        dict_lines = {}
        for key, item in self.dict_line.items():
            line = {
                "type_line": item.type_line.value,
                "polynomial_features": f"{item.type_line.value}_polynomial_features.pkl",
                "polynomial_regression": f"{item.type_line.value}_polynomial_regression.pkl",
                "left_border": item.left_border,
                "right_border": item.right_border,
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

    def load_graph(self):
        """Load graph data from a tar file.

        Args:
            None

        Returns:
            None
        """
        json_path = Paths.MODEL_DIRECTORY / f"{self.name}.json"
        with open(json_path, encoding="utf-8") as f:
            info_graph = json.load(f)

        if self.name != info_graph["name"]:
            raise ValueError("Error loading graph data")

        self.file_name = info_graph["file_name"]

        dict_lines = info_graph["dict_line"]
        for key, line in dict_lines.items():
            type_line = Type_line.give_enum_from_value(line["type_line"])
            left_border = line["left_border"]
            right_border = line["right_border"]
            polynomial_features = joblib.load(Paths.MODEL_DIRECTORY / self.name / line["polynomial_features"])
            polynomial_regression = joblib.load(Paths.MODEL_DIRECTORY / self.name / line["polynomial_regression"])

            item = Line(
                type_line=type_line,
                left_border=left_border,
                right_border=right_border,
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

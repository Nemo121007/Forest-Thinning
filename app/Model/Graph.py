import json
import tarfile
import re
from typing import Dict

from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score

from app.Model.Line import Line


class Graph:
    def __init__(self):
        self.dict_line: Dict[str, Line] = {}
        self.dict_model = {}

    def load_graph_in_tar(self, name_file: str):
        tar_path = f'../../data_line/{name_file}.tar'
        dataframes_dict = {}

        try:
            with tarfile.open(tar_path, 'r') as tar_ref:
                file_member = tar_ref.getmember(f'{name_file}/wpd.json')
                with tar_ref.extractfile(file_member) as file:
                    data = json.load(file)
                if 'datasetColl' not in data:
                    raise KeyError("Key 'datasetColl' is missing in the JSON data")

                data = data['datasetColl']

                for i in range(len(data)):
                    line = data[i]

                    all_x = []
                    all_y = []

                    # Извлечение данных для текущей линии
                    for item in line['data']:
                        all_x.append(item['value'][0])
                        all_y.append(item['value'][1])

                    if len(all_x) != len(all_y):
                        raise ValueError('The number of arguments X and Y does not match')

                    item = Line()
                    item.load_data(name=line['name'], X=all_x, Y=all_y)
                    # Сохраняем данные в словарь
                    if re.match(r'growth line \d+', line['name']):
                        item.load_data(start_parameter=all_y[0])
                    elif re.match(r'recovery line \d+', line['name']):
                        item.load_data(start_parameter=all_x[0])
                    else:
                        item.load_data(start_parameter=0)
                    dataframes_dict[line['name']] = item

        except FileNotFoundError:
            raise FileNotFoundError(f"File {tar_path} not found.")
        except KeyError:
            raise KeyError(f"File {name_file}/wpd.json not found in the archive.")

        self.dict_line = dataframes_dict

    def fit_models(self):
        for key, item in self.dict_line.items():
            try:
                item.fit_regression()
            except ValueError as e:
                print(f"Error fitting regression for {key}: {e}")

    def check_graph(self):
        plt.figure(figsize=(12, 7))

        for key, item in self.dict_line.items():
            plt.plot(item.X, item.Y, alpha=0.5, label=f'Original {key}', color='blue')

            symbol = ''
            list_change_symbol = []

            list_predict = []
            for i in range(len(item.X)):
                y_predict = item.predict_value(item.X[i], item.start_parameter)
                list_predict.append(y_predict)
                different = item.Y[i] - y_predict

                if different > 0 and symbol != '+' and abs(different) > 0.1:
                    symbol = '+'
                    list_change_symbol.append((item.X[i], different, symbol))
                    plt.scatter(item.X[i], y_predict, color='red', label='Точки')
                elif different < 0 and symbol != '-' and abs(different) > 0.1:
                    symbol = '-'
                    list_change_symbol.append((item.X[i], different, symbol))
                    plt.scatter(item.X[i], y_predict, color='red', label='Точки')
            with open(f'tmp_cache/{item.name}.json', 'w') as f:
                json.dump(list_change_symbol, f)
                print(f'Количество перегибов {item.name}: {len(list_change_symbol)}')

            plt.plot(item.X, list_predict, label=f'Predicted {key}', linestyle='--', color='black')

            mse_total = mean_squared_error(item.Y, list_predict)
            r2_total = r2_score(item.Y, list_predict)

            print(f"{item.name}: Общая MSE для обучающей выборки: {mse_total}")
            print(f"{item.name}: Общий R2 для обучающей выборки: {r2_total}")

        plt.show()


if __name__ == '__main__':
    a = Graph()
    a.load_graph_in_tar('pine_sorrel')
    #a.load_graph_in_tar('nortTaiga_pine_lingonberry')
    a.fit_models()
    a.check_graph()
    print(a)

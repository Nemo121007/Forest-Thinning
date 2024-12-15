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
        self.dict_test: Dict[str, Line] = {}

    def load_graph_in_tar(self, name_file: str):
        tar_path = f'../../data_line/{name_file}.tar'
        dataframes_dict: Dict[str, Line] = {}

        try:
            with tarfile.open(tar_path, 'r') as tar_ref:
                file_member = tar_ref.getmember(f'{name_file}/wpd.json')
                with tar_ref.extractfile(file_member) as file:
                    data = json.load(file)
                if 'datasetColl' not in data:
                    raise KeyError("Key 'datasetColl' is missing in the JSON data")

                data_list = list(data['datasetColl'])
                data_list.sort(key=lambda x: x['name'])

                for i in range(len(data_list)):
                    line = data_list[i]

                    all_x = []
                    all_y = []

                    # Извлечение данных для текущей линии
                    for item in line['data']:
                        all_x.append(item['value'][0])
                        all_y.append(item['value'][1])

                    if len(all_x) != len(all_y):
                        raise ValueError('The number of arguments X and Y does not match')

                    item = Line()
                    if re.match(r'growth line \d+', line['name']):
                        item.load_data(name=line['name'], X=all_x, Y=all_y, start_parameter=all_y[0])
                    elif re.match(r'recovery line \d+', line['name']):
                        item.load_data(name=line['name'], X=all_x, Y=all_y, start_parameter=all_x[0])
                    else:
                        item.load_data(name=line['name'], X=all_x, Y=all_y, start_parameter=0)
                    self.dict_test[line['name']] = item

                    item = Line()
                    # Сохраняем данные в словарь
                    if re.match(r'growth line \d+', line['name']):
                        if 'growth line' in dataframes_dict:
                            item = dataframes_dict['growth line']
                            item.append_data(X=all_x, Y=all_y, start_parameter=all_y[0])
                            continue
                        else:
                            item.load_data(name='growth line', X=all_x, Y=all_y, start_parameter=all_y[0])
                            dataframes_dict['growth line'] = item
                            continue
                    elif re.match(r'recovery line \d+', line['name']):
                        if 'recovery line' in dataframes_dict:
                            item = dataframes_dict['recovery line']
                            item.append_data(X=all_x, Y=all_y, start_parameter=all_x[0])
                            continue
                        else:
                            item.load_data(name='recovery line', X=all_x, Y=all_y, start_parameter=all_x[0])
                            dataframes_dict['recovery line'] = item
                            continue
                    else:
                        item.load_data(name=line['name'], X=all_x, Y=all_y, start_parameter=0)
                    dataframes_dict[line['name']] = item

        except FileNotFoundError:
            raise FileNotFoundError(f"File {tar_path} not found.")
        except KeyError as e:
            raise KeyError(f"Key error: {e}")
        except ValueError as e:
            raise ValueError(f"Value error: {e}")

        self.dict_line = dataframes_dict

    def fit_models(self):
        for key, item in self.dict_line.items():
            try:
                item.fit_regression()
            except ValueError as e:
                print(f"Error fitting regression for {key}: {e}")

    def check_graph(self):
        plt.figure(figsize=(15, 10))

        max_different = 0
        for key, item in self.dict_test.items():
            plt.plot(item.X, item.Y, alpha=0.5, label=f'Original {key}', color='blue')

            symbol = ''
            list_change_symbol = []

            list_predict = []
            for i in range(len(item.X)):
                if re.match(r'growth line \d+', item.name):
                    model = self.dict_line['growth line']
                elif re.match(r'recovery line \d+', item.name):
                    model = self.dict_line['recovery line']
                else:
                    model = self.dict_line[item.name]
                y_predict = model.predict_value(item.X[i], item.start_parameter[i])
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
                if max_different < abs(different):
                    max_different = abs(different)
            with open(f'tmp_cache/{item.name}.json', 'w') as f:
                json.dump(list_change_symbol, f)
                print(f'Количество перегибов {item.name}: {len(list_change_symbol)}')

            plt.plot(item.X, list_predict, label=f'Predicted {key}', linestyle='--', color='black')

            mse_total = mean_squared_error(item.Y, list_predict)
            r2_total = r2_score(item.Y, list_predict)

            print(f"{item.name}: Общая MSE для обучающей выборки: {mse_total}")
            print(f"{item.name}: Общий R2 для обучающей выборки: {r2_total}")

        print(f'Максимальная ошибка при аппроксимации: {max_different}')
        plt.show()


if __name__ == '__main__':
    a = Graph()
    # a.load_graph_in_tar('pine_sorrel')
    a.load_graph_in_tar('nortTaiga_pine_lingonberry')
    a.fit_models()
    a.check_graph()
    print(a)

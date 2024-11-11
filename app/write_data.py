import json
import re

import pandas as pd


def main_1():
    with open('../data_line/pine_sorrel/wpd.json', 'r') as f:
        data = json.load(f)

    data1 = data['datasetColl']
    data2 = data1[0]
    data3 = data2['data']

    b = []
    for i in range(len(data3)):
        a = data3[i]
        b.append(a["value"])

    df = pd.DataFrame(b, columns=['x', 'y'])
    print(df.head())

    df.to_json('../data_line/tmp_data_1.json', orient='records')


def main_2():
    with open('../data_line/pine_sorrel/wpd.json', 'r') as f:
        data = json.load(f)

    data = data['datasetColl']

    # Создаем пустой словарь для хранения DataFrame
    dataframes_dict = {}

    for i in range(len(data)):
        if re.match(r'growth line \d+', data[i]['name']):
            line = data[i]
            b = []

            # Извлечение данных для текущей линии
            for item in line['data']:
                b.append(item["value"])

            # Создаем DataFrame для текущей линии
            df = pd.DataFrame(b, columns=['x', 'y'])

            # Сохраняем DataFrame в словарь с ключом - названием линии
            dataframes_dict[line['name']] = df

    # Конвертируем DataFrame в словарь и сохраняем в JSON
    data_to_save = {name: df.to_dict(orient="list") for name, df in dataframes_dict.items()}

    with open('../data_line/tmp_data_2.json', 'w') as f:
        json.dump(data_to_save, f)

    print("Data successfully saved to tmp_data.json.")




if __name__ == '__main__':
    main_1()

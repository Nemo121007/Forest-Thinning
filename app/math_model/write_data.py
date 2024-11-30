import json
import re
import tarfile
import pandas as pd
"""
write_data.py

Описание:
    Данный файл содержит код для переписывания данных из архива .tar в промежуточные файлы tmp_data_d+ для 
    дальнейшего анализа
"""


def main_1():
    """Запись данных о первом графике в tmp_data_1.json"""
    with open('../../data_line/pine_sorrel/wpd.json', 'r') as f:
        data = json.load(f)

    data1 = data['datasetColl']
    data2 = data1[0]
    data3 = data2['data']

    b = []
    for i in range(len(data3)):
        a = data3[i]
        b.append(a["value"])

    df = pd.DataFrame(b, columns=['x', 'y'])

    df.to_json('../../data_line/tmp_data_1.json', orient='records')
    print("Data successfully saved to tmp_data_1.json.")


def main_2():
    """Запись данных о линиях роста из графиков в tmp_data_2.json"""
    with open('../../data_line/pine_sorrel/wpd.json', 'r') as f:
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

    with open('../../data_line/tmp_data_2.json', 'w') as f:
        json.dump(data_to_save, f)

    print("Data successfully saved to tmp_data_2.json.")


def main_3():
    """Запись данных о линиях роста из графиков в tmp_data_3.json"""
    with open('../../data_line/pine_sorrel/wpd.json', 'r') as f:
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
            dataframes_dict[line['name']] = {
                'name': line['name'],
                'data': df.to_dict(orient='list'),
                'start_point': df['y'][0]
            }

    with open('../../data_line/tmp_data_3.json', 'w') as f:
        json.dump(dataframes_dict, f)

    print("Data successfully saved to tmp_data_3.json.")


def main_4():
    """Запись данных о линиях роста и эталонной линии роста из графиков в tmp_data_4.json"""
    # Путь к архиву
    tar_path = '../../data_line/pine_sorrel.tar'

    # Распаковка архива и чтение файлов
    with tarfile.open(tar_path, 'r') as tar_ref:
        # Открыть файл из архива на чтение
        file_member = tar_ref.getmember('pine_sorrel/wpd.json')

        with tar_ref.extractfile(file_member) as file:
            data = json.load(file)

            data = data['datasetColl']

            # Создаем пустой словарь для хранения DataFrame
            dataframes_dict = {}

            for i in range(len(data)):
                if re.match(r'growth line \d+', data[i]['name']) or re.match(r'standard growth line', data[i]['name']):
                    line = data[i]
                    b = []

                    # Извлечение данных для текущей линии
                    for item in line['data']:
                        b.append(item["value"])

                    # Создаем DataFrame для текущей линии
                    df = pd.DataFrame(b, columns=['x', 'y'])

                    # Сохраняем DataFrame в словарь с ключом - названием линии
                    dataframes_dict[line['name']] = {
                        'name': line['name'],
                        'data': df.to_dict(orient='list'),
                        'start_point': df['y'][0]
                    }

            with open('../../data_line/tmp_data_4.json', 'w') as f:
                json.dump(dataframes_dict, f)

            print("Data successfully saved to tmp_data_4.json.")


def main_all_line():
    """Запись данных о всех линиях из графиков в tmp_data_all_line.json"""
    # Путь к архиву
    tar_path = '../../data_line/pine_sorrel.tar'

    # Распаковка архива и чтение файлов
    with tarfile.open(tar_path, 'r') as tar_ref:
        # Открыть файл из архива на чтение
        file_member = tar_ref.getmember('pine_sorrel/wpd.json')

        with tar_ref.extractfile(file_member) as file:
            data = json.load(file)

            data = data['datasetColl']

            # Создаем пустой словарь для хранения DataFrame
            dataframes_dict = {}

            for i in range(len(data)):
                line = data[i]
                b = []

                # Извлечение данных для текущей линии
                for item in line['data']:
                    b.append(item["value"])

                # Создаем DataFrame для текущей линии
                df = pd.DataFrame(b, columns=['x', 'y'])

                # Сохраняем DataFrame в словарь с ключом - названием линии
                if re.match(r'growth line \d+', data[i]['name']):
                    dataframes_dict[line['name']] = {
                        'name': line['name'],
                        'data': df.to_dict(orient='list'),
                        'start_point': df['y'][0]
                    }
                elif re.match(r'recovery line \d+', data[i]['name']):
                    dataframes_dict[line['name']] = {
                        'name': line['name'],
                        'data': df.to_dict(orient='list'),
                        'start_point': df['x'][0]
                    }
                else:
                    dataframes_dict[line['name']] = {
                        'name': line['name'],
                        'data': df.to_dict(orient='list'),
                        'start_point': 0
                    }

            with open('../../data_line/tmp_data_all_line.json', 'w') as f:
                json.dump(dataframes_dict, f)

            print("Data successfully saved to tmp_data_all_line.json.")


if __name__ == '__main__':
    main_1()
    main_2()
    main_3()
    main_4()
    main_all_line()

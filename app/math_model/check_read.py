import json
import pickle
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score


if __name__ == '__main__':
    # Загрузка JSON-данных из файла
    with open('../../data_line/tmp_data_3.json', 'r') as f:
        data = json.load(f)

    # Переменные для накопления всех данных
    all_x = []
    all_y0 = []
    all_y = []

    # Накопление всех данных для построения общей модели
    for key in data.keys():
        line = data[key]
        y0 = np.full(len(line['data']['x']), line['start_point'])  # Преобразуем y0 в массив
        x = np.array(line['data']['x'])
        y = np.array(line['data']['y'])

        # Сохранение данных
        all_x.extend(x)
        all_y0.extend(y0)
        all_y.extend(y)

    # Конвертируем в numpy массивы для модели
    X = np.column_stack((all_x, all_y0))
    y = np.array(all_y)

    # Восстановление объектов из файлов
    with open('poly_reg.pkl', 'rb') as f:
        loaded_poly_reg = pickle.load(f)

    with open('poly_features.pkl', 'rb') as f:
        loaded_poly_features = pickle.load(f)

    print("Модель и полиномиальные признаки восстановлены из файлов.")

    # Предсказание с использованием восстановленной модели
    # Оценка модели на основе исходных данных
    X_poly = loaded_poly_features.transform(X)
    y_train_pred = loaded_poly_reg.predict(X_poly)
    mse_total = mean_squared_error(y, y_train_pred)
    r2_total = r2_score(y, y_train_pred)

    print(f"Общая MSE для обучающей выборки: {mse_total}")
    print(f"Общий R2 для обучающей выборки: {r2_total}")
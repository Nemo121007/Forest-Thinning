import json
import pickle
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Функция для обучения полиномиальной регрессии
def polynomial_regression_two_vars(X, y, degree):
    """Полиномиальная регрессия от двух переменных заданной степени"""
    # Создаем полиномиальные признаки для двух переменных
    poly_features = PolynomialFeatures(degree=degree)
    X_poly = poly_features.fit_transform(X)

    # Линейная регрессия на полиномиальных признаках
    poly_reg = LinearRegression()
    poly_reg.fit(X_poly, y)

    return poly_reg, poly_features


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

    # Обучаем общую модель на основе всех данных
    degree = 4  # Задаем степень полинома
    poly_reg, poly_features = polynomial_regression_two_vars(X, y, degree)

    # Вычисляем предсказанные значения для исходных данных
    X_poly = poly_features.transform(X)
    y_pred = poly_reg.predict(X_poly)

    # Оценка модели на основе всех данных
    mse_total = mean_squared_error(y, y_pred)
    r2_total = r2_score(y, y_pred)

    print(f"Общая MSE для всех графиков: {mse_total}")
    print(f"Общий R2 для всех графиков: {r2_total}")

    # Сохранение объектов poly_reg и poly_features в файлы
    with open('poly_reg.pkl', 'wb') as f:
        pickle.dump(poly_reg, f)

    with open('poly_features.pkl', 'wb') as f:
        pickle.dump(poly_features, f)

    print("Модель и полиномиальные признаки сохранены в файлы.")

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

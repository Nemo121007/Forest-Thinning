import json
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import matplotlib.pyplot as plt
"""
search_degree_approximation.py

Описание:
    Данный файл содержит код проверки, какая степень полиномиальной аппроксимации даёт наилучший результат
"""


def polynomial_regression_two_vars(X, y, degree):
    """Полиномиальная регрессия для двух переменных"""
    poly_features = PolynomialFeatures(degree=degree)
    X_poly = poly_features.fit_transform(X)
    model = LinearRegression()
    model.fit(X_poly, y)
    return model, poly_features


def evaluate_model_for_degrees(data, list_train_line, degrees):
    """Оценивает модель для всех степеней из указанного интервала."""
    results = []

    # Накопление данных для обучения
    all_x, all_y0, all_y = [], [], []
    for key in list_train_line:
        line = data[key]
        y0 = np.full(len(line['data']['x']), line['start_point'])
        x = np.array(line['data']['x'])
        y = np.array(line['data']['y'])
        all_x.extend(x)
        all_y0.extend(y0)
        all_y.extend(y)

    # Конвертируем в numpy массивы
    X_train = np.column_stack((all_x, all_y0))
    y_train = np.array(all_y)

    # Накопление данных для тестирования
    all_x, all_y0, all_y = [], [], []
    for key in data.keys():
        if key not in list_train_line:
            line = data[key]
            y0 = np.full(len(line['data']['x']), line['start_point'])
            x = np.array(line['data']['x'])
            y = np.array(line['data']['y'])
            all_x.extend(x)
            all_y0.extend(y0)
            all_y.extend(y)

    X_test = np.column_stack((all_x, all_y0))
    y_test = np.array(all_y)

    # Оценка для каждой степени
    for degree in degrees:
        # Обучение модели
        model, poly_features = polynomial_regression_two_vars(X_train, y_train, degree)

        # Предсказание
        X_test_poly = poly_features.transform(X_test)
        y_pred = model.predict(X_test_poly)

        # Метрики
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        results.append((degree, mse, r2))

        print(f"Степень: {degree}, MSE: {mse:.4f}, R2: {r2:.4f}")

    return results


if __name__ == "__main__":
    # Загрузка данных
    with open('../../data_line/tmp_data_4.json', 'r') as f:
        data = json.load(f)

    # Линии для обучения
    list_train_line = ['growth line 1', 'growth line 3', 'growth line 6', 'growth line 9', 'standard growth line']

    # Интервал степеней для проверки
    degrees = range(1, 12)

    # Оценка модели
    results = evaluate_model_for_degrees(data, list_train_line, degrees)

    # Построение графика
    degrees, mses, r2s = zip(*results)

    plt.figure(figsize=(10, 6))
    plt.plot(degrees, mses, marker='o', label='MSE', color='red')
    plt.plot(degrees, r2s, marker='o', label='R^2', color='blue')
    plt.xlabel('Степень полинома')
    plt.ylabel('Метрика')
    plt.title('Зависимость метрик от степени полинома')
    plt.legend()
    plt.grid()
    plt.show()

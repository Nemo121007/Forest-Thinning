"""
search_degree_approximation.py

Описание:
    Данный файл содержит код проверки, какая степень полиномиальной аппроксимации даёт наилучший результат
"""

import json
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import matplotlib.pyplot as plt


def polynomial_regression_two_vars(X, y, degree):
    """Полиномиальная регрессия для двух переменных"""
    poly_features = PolynomialFeatures(degree=degree)
    X_poly = poly_features.fit_transform(X)
    model = LinearRegression()
    model.fit(X_poly, y)
    return model, poly_features


def evaluate_model_for_degrees(data, degrees):
    """Оценивает модель для всех степеней из указанного интервала."""
    results = []

    # Накопление данных для обучения
    all_x, all_y0, all_y = [], [], []
    for key in data.keys():
        line = data[key]
        y0 = np.full(len(line["data"]["x"]), line["start_point"])
        x = np.array(line["data"]["x"])
        y = np.array(line["data"]["y"])
        all_x.extend(x)
        all_y0.extend(y0)
        all_y.extend(y)

    # Конвертируем в numpy массивы
    X = np.column_stack((all_x, all_y0))
    y = np.array(all_y)

    # Оценка для каждой степени
    for degree in degrees:
        # Обучение модели
        model, poly_features = polynomial_regression_two_vars(X, y, degree)

        # Предсказание
        X_test_poly = poly_features.transform(X)
        y_pred = model.predict(X_test_poly)

        # Метрики
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)

        results.append((degree, mse, r2))

        print(f"Степень: {degree}, MSE: {mse:.4f}, R2: {r2:.4f}")

    return results


if __name__ == "__main__":
    # Загрузка данных
    with open("../../data_line/tmp_data_4.json", "r") as f:
        data = json.load(f)

    # Интервал степеней для проверки
    degrees = range(1, 15)

    # Оценка модели
    results = evaluate_model_for_degrees(data, degrees)

    # Построение графика
    degrees, mses, r2s = zip(*results)

    plt.figure(figsize=(10, 6))
    plt.plot(degrees, mses, marker="o", label="MSE", color="red")
    plt.plot(degrees, r2s, marker="o", label="R^2", color="blue")
    plt.xlabel("Степень полинома")
    plt.ylabel("Метрика")
    plt.title("Зависимость метрик от степени полинома")
    plt.legend()
    plt.grid()
    plt.show()

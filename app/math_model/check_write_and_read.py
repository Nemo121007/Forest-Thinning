"""Module for polynomial regression two vars given degree."""

import json
import pickle
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


def polynomial_regression_two_vars(X: list[float], y: list[float], degree: int) -> tuple:
    """Polynomial regression two vars given degree.

    Args:
        X (list[float]): list of x values
        y (list[float]): list of y values
        degree (int): degree of polynomial
    Returns:
        tuple: tuple of polynomial regression and polynomial features
    """
    poly_features = PolynomialFeatures(degree=degree)
    X_poly = poly_features.fit_transform(X)

    poly_reg = LinearRegression()
    poly_reg.fit(X_poly, y)

    return poly_reg, poly_features


if __name__ == "__main__":
    with open("../../data_line/tmp_data_3.json") as f:
        data = json.load(f)

    all_x = []
    all_y0 = []
    all_y = []

    for key in data.keys():
        line = data[key]
        y0 = np.full(len(line["data"]["x"]), line["start_point"])
        x = np.array(line["data"]["x"])
        y = np.array(line["data"]["y"])

        all_x.extend(x)
        all_y0.extend(y0)
        all_y.extend(y)

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
    with open("poly_reg.pkl", "wb") as f:
        pickle.dump(poly_reg, f)

    with open("poly_features.pkl", "wb") as f:
        pickle.dump(poly_features, f)

    print("Модель и полиномиальные признаки сохранены в файлы.")

    # Восстановление объектов из файлов
    with open("poly_reg.pkl", "rb") as f:
        loaded_poly_reg = pickle.load(f)

    with open("poly_features.pkl", "rb") as f:
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

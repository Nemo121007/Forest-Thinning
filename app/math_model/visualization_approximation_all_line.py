"""
visualization_approximation_all_line.py

Описание:
    Данный файл содержит код для расчёта полиномиальной регрессии от двух переменных для всех графиков 1 изображения
"""

import json
import numpy as np
import re
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score


def polynomial_regression_two_vars(X, y, degree):
    """Полиномиальная регрессия от двух переменных заданной степени"""
    # Создаем полиномиальные признаки для двух переменных
    poly_features = PolynomialFeatures(degree=degree)
    X_poly = poly_features.fit_transform(X)

    # Линейная регрессия на полиномиальных признаках
    poly_reg = LinearRegression()
    poly_reg.fit(X_poly, y)

    return poly_reg, poly_features


if __name__ == "__main__":
    list_pattern_line = [
        r"growth line \d+",
        r"recovery line \d+",
        "min level logging",
        "max level logging",
        "economic max line",
        "economic min line",
    ]
    # Загрузка JSON-данных из файла
    with open("../../data_line/tmp_data_all_line.json", "r") as f:
        data = json.load(f)

    # Построение графиков
    plt.figure(figsize=(10, 6))

    # Отображаем исходные данные для всех графиков
    for key in data.keys():
        line = data[key]
        y0 = np.full(len(line["data"]["x"]), line["start_point"])
        x = np.array(line["data"]["x"])
        y = np.array(line["data"]["y"])
        plt.plot(x, y, alpha=0.5, label=f"Original {key}", color="blue")

    # Накопление всех данных для построения общей модели
    for key in list_pattern_line:
        # Переменные для накопления всех данных
        all_x = []
        all_y0 = []
        all_y = []
        for i in data.keys():
            if re.match(pattern=key, string=data[i]["name"]):
                line = data[i]
                y0 = np.full(len(line["data"]["x"]), line["start_point"])  # Преобразуем y0 в массив
                x = np.array(line["data"]["x"])
                y = np.array(line["data"]["y"])

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

        print(f"Общая MSE для {key} графиков: {mse_total}")
        print(f"Общий R2 для {key} графиков: {r2_total}")

        plt.plot(X, y_pred, label=f"Predicted {key}", linestyle="--", color="black")

    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Полиномиальная регрессия")
    plt.legend()
    plt.grid()
    plt.show()

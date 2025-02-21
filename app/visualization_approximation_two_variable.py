import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score


def polynomial_regression_two_vars(X, y, degree):
    # Создаем полиномиальные признаки для двух переменных
    poly_features = PolynomialFeatures(degree=degree)
    X_poly = poly_features.fit_transform(X)

    # Линейная регрессия на полиномиальных признаках
    poly_reg = LinearRegression()
    poly_reg.fit(X_poly, y)

    return poly_reg, poly_features


if __name__ == "__main__":
    # Загрузка JSON-данных из файла
    with open("../data_line/tmp_data_3.json", "r") as f:
        data = json.load(f)

    # Переменные для накопления всех данных
    all_x = []
    all_y0 = []
    all_y = []

    # Накопление всех данных для построения общей модели
    for key in data.keys():
        line = data[key]
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

    print(f"Общая MSE для всех графиков: {mse_total}")
    print(f"Общий R2 для всех графиков: {r2_total}")

    # Построение графиков
    plt.figure(figsize=(10, 6))

    # Отображаем исходные данные для всех графиков
    for key in data.keys():
        line = data[key]
        y0 = np.full(len(line["data"]["x"]), line["start_point"])
        x = np.array(line["data"]["x"])
        y = np.array(line["data"]["y"])
        plt.scatter(x, y, alpha=0.5, label=f"Original {key}")

        # Предсказания на основе общей модели для текущего графика
        X_curr = np.column_stack((x, y0))
        X_curr_poly = poly_features.transform(X_curr)
        y_curr_pred = poly_reg.predict(X_curr_poly)
        plt.plot(x, y_curr_pred, label=f"Predicted {key}", linestyle="--")

    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(
        f"Полиномиальная регрессия (степень {degree}) для всех графиков\nMSE: {mse_total:.4f}, R2: {r2_total:.4f}"
    )
    plt.legend()
    plt.show()

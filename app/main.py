import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score
from scipy.optimize import curve_fit


def linear_regression(x, y):
    lin_reg = LinearRegression()
    lin_reg.fit(x.reshape(-1, 1), y)
    y_predict = lin_reg.predict(x.reshape(-1, 1))

    # Вычисление метрик
    mse = mean_squared_error(y, y_predict)
    r2 = r2_score(y, y_predict)
    print(f"Линейная регрессия — MSE: {mse}, R2: {r2}")

    return y_predict


def polynomial_regression_degree(x, y, degree):
    poly_features = PolynomialFeatures(degree=degree)
    x_poly = poly_features.fit_transform(x.reshape(-1, 1))
    poly_reg = LinearRegression()
    poly_reg.fit(x_poly, y)
    y_pred = poly_reg.predict(x_poly)

    # Вычисление метрик
    mse = mean_squared_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    print(f"Полиномиальная регрессия (степень {degree}) — MSE: {mse}, R2: {r2}")

    return y_pred


# Экспоненциальная функция
def _exponential_model(x, a, b, c):
    return a * np.exp(b * x) + c


def exponential_approximation(x, y):
    # Подбор параметров
    try:
        popt, _ = curve_fit(_exponential_model, x, y, maxfev=10000)
        y_pred = _exponential_model(x, *popt)

        # Вычисление метрик
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        print(f"Экспоненциальная аппроксимация — MSE: {mse}, R2: {r2}")
        return y_pred

    except RuntimeError:
        print("Экспоненциальная модель не подходит для этих данных.")


if __name__ == "__main__":
    # Загрузка JSON-данных из файла
    with open("../data_line/tmp_data_1.json", "r") as f:
        data = json.load(f)

    # Преобразование в DataFrame
    df = pd.json_normalize(data)

    x = np.array(df["x"])
    y = np.array(df["y"])

    fig = plt.figure()

    ax1 = fig.add_subplot(2, 3, 1)
    ax2 = fig.add_subplot(2, 3, 2)
    ax3 = fig.add_subplot(2, 3, 3)
    ax4 = fig.add_subplot(2, 3, 4)
    ax5 = fig.add_subplot(2, 3, 5)
    ax6 = fig.add_subplot(2, 3, 6)

    y_predict_linear_regression = linear_regression(x, y)

    ax1.scatter(x, y, color="blue", label="Data Points")
    ax1.plot(x, y_predict_linear_regression, color="red", label="Linear Regression")
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.set_title("Линейная регрессия")
    ax1.legend()

    y_predict_polynomial_regression_degree_2 = polynomial_regression_degree(x, y, 2)

    ax2.scatter(x, y, color="blue", label="Data Points")
    ax2.plot(
        x,
        y_predict_polynomial_regression_degree_2,
        color="green",
        label="Polynomial Regression (degree 2)",
    )
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    ax2.set_title("Полиномиальная регрессия (степень 2)")
    ax2.legend()

    y_predict_polynomial_regression_degree_3 = polynomial_regression_degree(x, y, 3)

    ax3.scatter(x, y, color="blue", label="Data Points")
    ax3.plot(
        x,
        y_predict_polynomial_regression_degree_3,
        color="green",
        label="Polynomial Regression (degree 3)",
    )
    ax3.set_xlabel("x")
    ax3.set_ylabel("y")
    ax3.set_title("Полиномиальная регрессия (степень 3)")
    ax3.legend()

    y_predict_polynomial_regression_degree_4 = polynomial_regression_degree(x, y, 4)

    ax4.scatter(x, y, color="blue", label="Data Points")
    ax4.plot(
        x,
        y_predict_polynomial_regression_degree_4,
        color="green",
        label="Polynomial Regression (degree 4)",
    )
    ax4.set_xlabel("x")
    ax4.set_ylabel("y")
    ax4.set_title("Полиномиальная регрессия (степень 4)")
    ax4.legend()

    y_predict_polynomial_regression_degree_5 = polynomial_regression_degree(x, y, 5)

    ax5.scatter(x, y, color="blue", label="Data Points")
    ax5.plot(
        x,
        y_predict_polynomial_regression_degree_5,
        color="green",
        label="Polynomial Regression (degree 5)",
    )
    ax5.set_xlabel("x")
    ax5.set_ylabel("y")
    ax5.set_title("Полиномиальная регрессия (степень 5)")
    ax5.legend()

    y_predict_exponential_fit = exponential_approximation(x, y)

    ax6.scatter(x, y, color="blue", label="Data Points")
    ax6.plot(x, y_predict_exponential_fit, color="orange", label="Exponential Fit")
    ax6.set_xlabel("x")
    ax6.set_ylabel("y")
    ax6.set_title("Экспоненциальная аппроксимация")
    ax6.legend()

    plt.show()

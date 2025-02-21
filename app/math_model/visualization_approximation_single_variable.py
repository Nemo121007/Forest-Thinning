import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score
from scipy.optimize import curve_fit

"""
visualization_approximation_single_variable.py

Описание:
    Данный файл содержит код различных видов аппроксимации и сравнения их эффективности
"""


def linear_regression(x, y):
    """Линейная регрессия"""
    lin_reg = LinearRegression()
    lin_reg.fit(x.reshape(-1, 1), y)
    y_predictict = lin_reg.predict(x.reshape(-1, 1))

    # Вычисление метрик
    mse = mean_squared_error(y, y_predictict)
    r2 = r2_score(y, y_predictict)
    print(f"Линейная регрессия — MSE: {mse}, R2: {r2}")

    return y_predictict


def polynomial_regression_degree(x, y, degree):
    """Полиномиальная регрессия заданной степени"""
    poly_features = PolynomialFeatures(degree=degree)
    x_poly = poly_features.fit_transform(x.reshape(-1, 1))
    poly_reg = LinearRegression()
    poly_reg.fit(x_poly, y)
    y_predict = poly_reg.predict(x_poly)

    # Вычисление метрик
    mse = mean_squared_error(y, y_predict)
    r2 = r2_score(y, y_predict)
    print(f"Полиномиальная регрессия (степень {degree}) — MSE: {mse}, R2: {r2}")

    return y_predict


def _exponential_model(x, a, b, c):
    """Функция вычисления экспоненты"""
    return a * np.exp(b * x) + c


def exponential_approximation(x, y):
    """Экспоненциальная регрессия"""
    # Подбор параметров
    try:
        popt, _ = curve_fit(_exponential_model, x, y, maxfev=10000)
        y_predict = _exponential_model(x, *popt)

        # Вычисление метрик
        mse = mean_squared_error(y, y_predict)
        r2 = r2_score(y, y_predict)
        print(f"Экспоненциальная аппроксимация — MSE: {mse}, R2: {r2}")
        return y_predict

    except RuntimeError:
        print("Экспоненциальная модель не подходит для этих данных.")


def generalized_logarithmic_function(x, a, b, p):
    """Обобщённая логарифмическая функция с параметром степени p"""
    return a * (np.log(x) ** p) + b


def logarithmic_approximation_with_power(x, y, p):
    """Логарифмическая аппроксимация с фиксированной степенью логарифма"""
    try:
        # Вспомогательная функция для curve_fit с фиксированным p
        def fixed_power_logarithmic(x, a, b):
            return generalized_logarithmic_function(x, a, b, p)

        # Подбор параметров a и b
        popt, _ = curve_fit(fixed_power_logarithmic, x, y, maxfev=10000)
        y_pred = fixed_power_logarithmic(x, *popt)

        # Вычисление метрик
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        print(
            f"Логарифмическая аппроксимация с фиксированной степенью p={p} — MSE: {mse}, R2: {r2}"
        )
        print(f"Оптимальные параметры: a = {popt[0]}, b = {popt[1]}")
        return y_pred, popt
    except RuntimeError:
        print("Логарифмическая аппроксимация не подходит для данных.")
        return None, None


def polynomial_function(x, y, degree):
    """Строит полиномиальную регрессию и возвращает модель и преобразованные признаки."""
    poly_features = PolynomialFeatures(degree=degree)
    x_poly = poly_features.fit_transform(x.reshape(-1, 1))
    model = LinearRegression()
    model.fit(x_poly, y)
    return model, poly_features


def rational_polynomial_function(x, y, degree):
    """
    Строит аппроксимацию функции вида (P1(x) / P2(x)),
    где P1 и P2 — полиномиальные регрессии степени degree.
    """
    # Этап 1: Оптимизация числителя
    model_num, poly_features_num = polynomial_function(x, y, degree)
    x_poly_num = poly_features_num.transform(x.reshape(-1, 1))
    y_num = model_num.predict(x_poly_num)

    # Этап 2: Оптимизация знаменателя
    # Целевое значение: разница между реальными значениями и предсказанным числителем
    residuals = y - y_num
    model_den, poly_features_den = polynomial_function(
        x, residuals + 1, degree
    )  # Добавляем 1 для стабильности
    x_poly_den = poly_features_den.transform(x.reshape(-1, 1))
    y_den = model_den.predict(x_poly_den)

    # Избегаем деления на ноль
    y_den = np.where(np.abs(y_den) < 1e-6, 1e-6, y_den)

    # Итоговая рациональная функция
    y_pred = y_num / y_den

    # Вычисление метрик
    mse = mean_squared_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    print(
        f"Рациональная функция (P1/P2) (степень {degree}) — MSE: {mse:.4f}, R2: {r2:.4f}"
    )

    return y_pred


if __name__ == "__main__":
    # Загрузка JSON-данных из файла
    with open("../../data_line/tmp_data_1.json", "r") as f:
        data = json.load(f)

    # Преобразование в DataFrame
    df = pd.json_normalize(data)

    x = np.array(df["x"])
    y = np.array(df["y"])

    fig = plt.figure()

    ax1 = fig.add_subplot(3, 3, 1)
    ax2 = fig.add_subplot(3, 3, 2)
    ax3 = fig.add_subplot(3, 3, 3)
    ax4 = fig.add_subplot(3, 3, 4)
    ax5 = fig.add_subplot(3, 3, 5)
    ax6 = fig.add_subplot(3, 3, 6)
    ax7 = fig.add_subplot(3, 3, 7)
    ax8 = fig.add_subplot(3, 3, 8)
    ax9 = fig.add_subplot(3, 3, 9)

    y_predict_linear_regression = linear_regression(x, y)

    ax1.plot(x, y, color="blue", label="Data Points")
    ax1.plot(x, y_predict_linear_regression, color="black", label="Linear Regression")
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    # ax1.set_title('Линейная регрессия')
    ax1.legend()

    y_predict_polynomial_regression_degree_2 = polynomial_regression_degree(x, y, 2)

    ax2.plot(x, y, color="blue", label="Data Points")
    ax2.plot(
        x,
        y_predict_polynomial_regression_degree_2,
        color="black",
        label="Polynomial Regression (degree 2)",
    )
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    # ax2.set_title('Полиномиальная регрессия (степень 2)')
    ax2.legend()

    y_predict_polynomial_regression_degree_3 = polynomial_regression_degree(x, y, 3)

    ax3.plot(x, y, color="blue", label="Data Points")
    ax3.plot(
        x,
        y_predict_polynomial_regression_degree_3,
        color="black",
        label="Polynomial Regression (degree 3)",
    )
    ax3.set_xlabel("x")
    ax3.set_ylabel("y")
    # ax3.set_title('Полиномиальная регрессия (степень 3)')
    ax3.legend()

    y_predict_polynomial_regression_degree_4 = polynomial_regression_degree(x, y, 4)

    ax4.plot(x, y, color="blue", label="Data Points")
    ax4.plot(
        x,
        y_predict_polynomial_regression_degree_4,
        color="black",
        label="Polynomial Regression (degree 4)",
    )
    ax4.set_xlabel("x")
    ax4.set_ylabel("y")
    # ax4.set_title('Полиномиальная регрессия (степень 4)')
    ax4.legend()

    y_predict_exponential_fit = exponential_approximation(x, y)

    ax5.plot(x, y, color="blue", label="Data Points")
    ax5.plot(x, y_predict_exponential_fit, color="black", label="Exponential Fit")
    ax5.set_xlabel("x")
    ax5.set_ylabel("y")
    # ax5.set_title('Экспоненциальная аппроксимация')
    ax5.legend()

    degree = 1
    y_pred, params = logarithmic_approximation_with_power(x, y, degree)

    ax6.plot(x, y, color="blue", label="Data Points")
    if y_pred is not None:
        ax6.plot(x, y_pred, color="black", label=f"Logarithmic Fit {degree}")
    ax6.set_xlabel("x")
    ax6.set_ylabel("y")
    # ax6.set_title(f'Логарифмическая аппроксимация (степень {degree})')
    ax6.legend()

    degree = 2
    y_pred, params = logarithmic_approximation_with_power(x, y, degree)

    ax7.plot(x, y, color="blue", label="Data Points")
    if y_pred is not None:
        ax7.plot(x, y_pred, color="black", label=f"Logarithmic Fit {degree}")
    # ax7.set_title(f'Логарифмическая аппроксимация (степень {degree})')
    ax7.set_xlabel("x")
    ax7.set_ylabel("y")
    ax7.legend()

    degree = 2
    y_rational = rational_polynomial_function(x, y, degree)

    ax8.plot(x, y, color="blue", label="Data Points")
    ax8.plot(
        x,
        y_rational,
        color="black",
        label=f"Rational Function (P1/P2), degree {degree}",
    )
    ax8.set_xlabel("x")
    ax8.set_ylabel("y")
    # ax8.set_title(f'Рациональная функция: деление полинома на полином степени {degree}')
    ax8.legend()

    degree = 3
    y_rational = rational_polynomial_function(x, y, degree)

    ax9.plot(x, y, color="blue", label="Data Points")
    ax9.plot(
        x,
        y_rational,
        color="black",
        label=f"Rational Function (P1/P2), degree {degree}",
    )
    ax9.set_xlabel("x")
    ax9.set_ylabel("y")
    # ax9.set_title(f'Рациональная функция: деление полинома на полином степени {degree}')
    ax9.legend()

    plt.show()

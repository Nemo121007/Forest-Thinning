from typing import List
import numpy as np
from scipy.interpolate import UnivariateSpline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression


class Line:
    _borders: List[int]
    _border_sizes: List[float]
    _spline_model: UnivariateSpline

    def __init__(self,
                 list_polynomial_features: List[PolynomialFeatures] = None,
                 list_polynomial_regression: List[LinearRegression] = None,
                 name: str = None,
                 X: list = None,
                 Y: list = None,
                 start_parameter: List[float] = None):
        # Инициализация атрибутов экземпляра
        self.list_polynomial_features = list_polynomial_features or []
        self.list_polynomial_regression = list_polynomial_regression or []
        self.name = name
        self.X = np.array(X) if X else None
        self.Y = np.array(Y) if Y else None
        self.start_parameter = start_parameter or []

        # Инициализация списков и границ
        self._borders = []
        self._border_sizes = []

    def load_data(self,
                  list_polynomial_features: PolynomialFeatures = None,
                  list_polynomial_regression: LinearRegression = None,
                  name: str = None,
                  X: list = None,
                  Y: list = None,
                  start_parameter: List[float] = None):
        """Метод для загрузки данных в экземпляр класса Line"""
        if list_polynomial_features is not None:
            self.list_polynomial_features = list_polynomial_features
        if list_polynomial_regression is not None:
            self.list_polynomial_regression = list_polynomial_regression
        if name is not None:
            self.name = name
        if X is not None and Y is not None:
            # Сортируем X и переставляем Y так, чтобы соответствия сохранились
            sorted_indices = np.argsort(X)  # Индексы для сортировки X
            self.X = np.array(X)[sorted_indices]  # Сортируем X
            self.Y = np.array(Y)[sorted_indices]  # Переставляем Y в соответствии с сортировкой X

            n = len(X)
            # Делим данные на три сегмента
            self._borders = [0, n // 3, 2 * (n // 3), n]
            self._border_sizes = [X[b] for b in self._borders[1:-1]]
        if start_parameter is not None:
            start_parameter = [start_parameter] * len(X)
            self.start_parameter = start_parameter

    @staticmethod
    def _polynomial_regression_two_vars(X, y, degree):
        """Полиномиальная регрессия от двух переменных заданной степени"""
        polynomial_features = PolynomialFeatures(degree=degree)
        x_polynomial = polynomial_features.fit_transform(X)

        polynomial_reg = LinearRegression()
        polynomial_reg.fit(x_polynomial, y)

        return polynomial_reg, polynomial_features

    def fit_regression(self):
        if not self.start_parameter and self.start_parameter != 0:
            raise ValueError('Incorrect value start_parameter')
        if self.X is None or len(self.X) == 0:
            raise ValueError('Incorrect value X')
        if self.Y is None or len(self.Y) == 0:
            raise ValueError('Incorrect value Y')
        if len(self.X) != len(self.Y):
            raise ValueError('The size does not match X and Y')

        degree = 4  # Задаем степень полинома

        overlap = int(0.1 * len(self.X))  # 10% перекрытия

        # Формируем список сегментов с перекрытием
        segments = [
            (self.X[max(0, self._borders[i] - overlap):min(len(self.X), self._borders[i + 1] + overlap)],
             self.Y[max(0, self._borders[i] - overlap):min(len(self.Y), self._borders[i + 1] + overlap)],
             self.start_parameter[
             max(0, self._borders[i] - overlap):min(len(self.start_parameter), self._borders[i + 1] + overlap)])
            for i in range(len(self._borders) - 1)
        ]

        # Обучаем модели для каждого сегмента
        for x_segment, y_segment, start_segment in segments:
            x_combined = np.column_stack((x_segment, start_segment))
            polynomial_reg, polynomial_features = self._polynomial_regression_two_vars(x_combined, y_segment, degree)
            self.list_polynomial_regression.append(polynomial_reg)
            self.list_polynomial_features.append(polynomial_features)

    def predict_value(self, x: float, start_point: float) -> float:
        """
        Предсказывает значение y на основе x и стартового параметра.

        :param x: Значение переменной x (число).
        :param start_point: Стартовый параметр (число).
        :return: Предсказанное значение y (число).
        """
        combined_x = np.array([[x, start_point]])

        # Определяем, в каком сегменте находится x
        if x < self._border_sizes[0]:
            model_index = 0
        elif x < self._border_sizes[1]:
            model_index = 1
        else:
            model_index = 2

        # Выбираем соответствующую модель и полиномиальные признаки
        polynomial_features = self.list_polynomial_features[model_index]
        polynomial_regression = self.list_polynomial_regression[model_index]

        # Преобразуем данные в полиномиальные признаки
        x_polynomial = polynomial_features.transform(combined_x)

        # Предсказание на основе обученной модели
        y = polynomial_regression.predict(x_polynomial)

        return float(y[0])

    def fit_spline(self):
        # Сортируем данные по X
        sorted_indices = np.argsort(self.X)
        sorted_x = self.X[sorted_indices]
        sorted_y = self.Y[sorted_indices]

        # Создаём модель сплайна
        self._spline_model = UnivariateSpline(sorted_x, sorted_y, k=5)

    def predict_spline(self, x: float) -> float:
        return self._spline_model(x)

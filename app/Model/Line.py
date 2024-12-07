from typing import List
import numpy as np
from scipy.interpolate import UnivariateSpline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression


class Line:
    _borders: List[int]
    _border_sizes: List[float]
    _left_border: float
    _right_border: float
    _spline_model: UnivariateSpline

    def __init__(self,
                 list_polynomial_features: List[PolynomialFeatures] = None,
                 list_polynomial_regression: List[LinearRegression] = None,
                 name: str = None,
                 X: list = None,
                 Y: list = None,
                 start_parameter: List[float] = None):
                 start_parameter: float = None):
        if (X is not None) or (Y is not None) or (start_parameter is not None):
            if (X is None) or (Y is None) or (start_parameter is None):
                raise ValueError("X, Y, and start_parameter must all be provided")
            elif len(X) != len(Y):
                raise ValueError('Incorrect len X or Y')
        # Инициализация атрибутов экземпляра
        self.list_polynomial_features: List[PolynomialFeatures] = list_polynomial_features or []
        self.list_polynomial_regression: List[LinearRegression] = list_polynomial_regression or []
        self.name: str = name
        self.X: np.array = np.array(X) if X else None
        self.Y: np.array = np.array(Y) if Y else None
        if X is not None:
            self.start_parameter: np.array = np.array([start_parameter] * len(X))

        # Инициализация списков и границ
        self._borders = []
        self._border_sizes = []

        if X is not None:
            self._left_border = X[0]
            self._right_border = X[-1]

    def load_data(self,
                  list_polynomial_features: List[PolynomialFeatures] = None,
                  list_polynomial_regression: List[LinearRegression] = None,
                  name: str = None,
                  X: list[float] = None,
                  Y: list[float] = None,
                  start_parameter: float = None):
        """Метод для загрузки данных в экземпляр класса Line"""
        if (X is not None) or (Y is not None) or (start_parameter is not None):
            if (X is None) or (Y is None) or (start_parameter is None):
                raise ValueError("X, Y, and start_parameter must all be provided")
            elif len(X) != len(Y):
                raise ValueError('Incorrect len X or Y')

        if list_polynomial_features is not None:
            self.list_polynomial_features = list_polynomial_features
        if list_polynomial_regression is not None:
            self.list_polynomial_regression = list_polynomial_regression
        if name is not None:
            self.name = name
        if X is not None:
            self.X = np.array(X)
            n = len(X)
            # Делим данные на три сегмента
            self._borders = [0, n // 3, 2 * (n // 3), n]
            self._border_sizes = [X[b] for b in self._borders[1:-1]]

            self._left_border = X[0]
            self._right_border = X[-1]
        if Y is not None:
            self.Y = np.array(Y)
        if (start_parameter is not None) and (X is not None):
            self.start_parameter = np.array([start_parameter] * len(X))

        self._recalculate_borders()

    def append_data(self,
                    X: list[float],
                    Y: list[float],
                    start_parameter: float):
        """
        Добавляет новые данные к текущим массивам X, Y и start_parameter.

        :param X: Список значений X.
        :param Y: Список значений Y.
        :param start_parameter: Стартовый параметр, добавляемый ко всем новым данным.
        :raises ValueError: Если длины X и Y не совпадают.
        :raises AttributeError: Если self.X или self.Y не инициализированы.
        """
        if (X is not None) or (Y is not None) or (start_parameter is not None):
            if (X is None) or (Y is None) or (start_parameter is None):
                raise ValueError("X, Y, and start_parameter must all be provided")
            elif len(X) != len(Y):
                raise ValueError('Incorrect len X or Y')

        # Преобразуем списки в массивы NumPy
        X = np.array(X)
        Y = np.array(Y)
        new_start_parameter = np.full(len(X), start_parameter)

        # Объединяем существующие данные с новыми
        self.X = np.concatenate((self.X, X))
        self.Y = np.concatenate((self.Y, Y))
        self.start_parameter = np.concatenate((self.start_parameter, new_start_parameter))

        # Сортируем данные по X
        sorted_indices = np.argsort(self.X)
        self.X = self.X[sorted_indices]
        self.Y = self.Y[sorted_indices]
        self.start_parameter = self.start_parameter[sorted_indices]

        # Обновляем границы
        self._left_border = float(self.X[0])
        self._right_border = float(self.X[-1])

        self._recalculate_borders()

    def _recalculate_borders(self):
        n = len(self.X)
        self._borders = [0, n // 3, 2 * (n // 3), n]
        self._border_sizes = [float(self.X[b]) for b in self._borders[1:-1]]

    @staticmethod
    def _polynomial_regression_two_vars(X, y, degree):
        """Полиномиальная регрессия от двух переменных заданной степени"""
        polynomial_features = PolynomialFeatures(degree=degree)
        x_polynomial = polynomial_features.fit_transform(X)

        polynomial_reg = LinearRegression()
        polynomial_reg.fit(x_polynomial, y)

        return polynomial_reg, polynomial_features

    def fit_regression(self):
        if self.start_parameter is None or len(self.start_parameter) == 0:
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
        if not (self._left_border <= x <= self._right_border):
            raise ValueError('x is out of range')

        combined_x = np.array([[x, start_point]])

        # Определяем, в каком сегменте находится x
        if x <= self._border_sizes[0]:
            model_index = 0
        elif x <= self._border_sizes[1]:
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

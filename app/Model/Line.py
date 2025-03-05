"""Module for working with a line."""

import numpy as np
from scipy.interpolate import UnivariateSpline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression


class Line:
    """Class containing the data and methods for working with a line.

    Attributes:
        list_polynomial_features (list[PolynomialFeatures]): list of polynomial features
        list_polynomial_regression (list[LinearRegression]): list of polynomial regression
        name (str): name of line
        X (list): list of x values
        Y (list): list of y values
        start_parameter (list[float]): start parameter
        _borders (list[int]): list of borders
        _border_sizes (list[float]): list of border sizes
        _left_border (float): left border
        _right_border (float): right border
        _spline_model (UnivariateSpline): spline model

    Returns:
        None
    """

    _borders: list[int]
    _border_sizes: list[float]
    _left_border: float
    _right_border: float
    _spline_model: UnivariateSpline

    def __init__(
        self,
        list_polynomial_features: list[PolynomialFeatures] = None,
        list_polynomial_regression: list[LinearRegression] = None,
        name: str = None,
        X: list = None,
        Y: list = None,
        start_parameter: list[float] = None,
    ):
        """Initialization of the Line class.

        Args:
            list_polynomial_features (list[PolynomialFeatures], optional): list of polynomial features.
            Defaults to None.
            list_polynomial_regression (list[LinearRegression], optional): list of polynomial regression.
            Defaults to None.
            name (str, optional): name of line. Defaults to None.
            X (list, optional): list of x values. Defaults to None.
            Y (list, optional): list of y values. Defaults to None.
            start_parameter (list[float], optional): start parameter. Defaults to None.

        Raises:
            ValueError: X, Y, and start_parameter must all be provided
            ValueError: Incorrect len X or Y

        Returns:
            None
        """
        if (X is not None) or (Y is not None) or (start_parameter is not None):
            if (X is None) or (Y is None) or (start_parameter is None):
                raise ValueError("X, Y, and start_parameter must all be provided")
            elif len(X) != len(Y):
                raise ValueError("Incorrect len X or Y")

        self.list_polynomial_features: list[PolynomialFeatures] = list_polynomial_features or []
        self.list_polynomial_regression: list[LinearRegression] = list_polynomial_regression or []
        self.name: str = name
        self.X: np.array = np.array(X) if X else None
        self.Y: np.array = np.array(Y) if Y else None
        if X is not None:
            self.start_parameter: np.array = np.array([start_parameter] * len(X))

        self._borders = []
        self._border_sizes = []

        if X is not None:
            self._left_border = X[0]
            self._right_border = X[-1]

    def load_data(
        self,
        list_polynomial_features: list[PolynomialFeatures] = None,
        list_polynomial_regression: list[LinearRegression] = None,
        name: str = None,
        X: list[float] = None,
        Y: list[float] = None,
        start_parameter: float = None,
    ):
        """Download data in example class Line.

        Args:
            list_polynomial_features (list[PolynomialFeatures], optional): list of polynomial features.
            Defaults to None.
            list_polynomial_regression (list[LinearRegression], optional): list of polynomial regression.
            Defaults to None.
            name (str, optional): name of line. Defaults to None.
            X (list[float], optional): list of x values. Defaults to None.
            Y (list[float], optional): list of y values. Defaults to None.
            start_parameter (float, optional): start parameter. Defaults to None.

        Raises:
            ValueError: X, Y, and start_parameter must all be provided
            ValueError: Incorrect len X or Y

        Returns:
            None
        """
        if (X is not None) or (Y is not None) or (start_parameter is not None):
            if (X is None) or (Y is None) or (start_parameter is None):
                raise ValueError("X, Y, and start_parameter must all be provided")
            elif len(X) != len(Y):
                raise ValueError("Incorrect len X or Y")

        if list_polynomial_features is not None:
            self.list_polynomial_features = list_polynomial_features
        if list_polynomial_regression is not None:
            self.list_polynomial_regression = list_polynomial_regression
        if name is not None:
            self.name = name
        if X is not None:
            self.X = np.array(X)
            n = len(X)
            # split on 3 parts
            # TODO: check alien variant
            self._borders = [0, n // 3, 2 * (n // 3), n]
            self._border_sizes = [X[b] for b in self._borders[1:-1]]

            self._left_border = X[0]
            self._right_border = X[-1]
        if Y is not None:
            self.Y = np.array(Y)
        if (start_parameter is not None) and (X is not None):
            self.start_parameter = np.array([start_parameter] * len(X))

        self._recalculate_borders()

    def append_data(self, X: list[float], Y: list[float], start_parameter: float):
        """Add new data in current array X, Y and start_parameter.

        Args:
            X (list[float]): list of x values
            Y (list[float]): list of y values
            start_parameter (float): start parameter

        Returns:
            None
        """
        if (X is not None) or (Y is not None) or (start_parameter is not None):
            if (X is None) or (Y is None) or (start_parameter is None):
                raise ValueError("X, Y, and start_parameter must all be provided")
            elif len(X) != len(Y):
                raise ValueError("Incorrect len X or Y")

        # in array NumPy
        x = np.array(X)
        y = np.array(Y)
        new_start_parameter = np.full(len(x), start_parameter)

        self.X = np.concatenate((self.X, x))
        self.Y = np.concatenate((self.Y, y))
        self.start_parameter = np.concatenate((self.start_parameter, new_start_parameter))

        # sort on X
        sorted_indices = np.argsort(self.X)
        self.X = self.X[sorted_indices]
        self.Y = self.Y[sorted_indices]
        self.start_parameter = self.start_parameter[sorted_indices]

        # Update borders
        self._left_border = float(self.X[0])
        self._right_border = float(self.X[-1])

        self._recalculate_borders()

    def _recalculate_borders(self):
        """Recalculate borders.

        Args:
            None

        Returns:
            None
        """
        n = len(self.X)
        self._borders = [0, n // 3, 2 * (n // 3), n]
        self._border_sizes = [float(self.X[b]) for b in self._borders[1:-1]]

    @staticmethod
    def _polynomial_regression_two_vars(X: list[float], y: list[float], degree: int) -> tuple:
        """Polynomial regression on two vars of a given degree.

        Args:
            X (list[float]): list of x values
            y (list[float]): list of y values
            degree (int): degree of polynomial

        Returns:
            tuple: tuple of polynomial regression and polynomial features
        """
        polynomial_features = PolynomialFeatures(degree=degree)
        x_polynomial = polynomial_features.fit_transform(X)

        polynomial_reg = LinearRegression()
        polynomial_reg.fit(x_polynomial, y)

        return polynomial_reg, polynomial_features

    def fit_regression(self):
        """Fit regression model for all segments.

        :Args:
            None

        Returns:
            None
        """
        if self.start_parameter is None or len(self.start_parameter) == 0:
            raise ValueError("Incorrect value start_parameter")
        if self.X is None or len(self.X) == 0:
            raise ValueError("Incorrect value X")
        if self.Y is None or len(self.Y) == 0:
            raise ValueError("Incorrect value Y")
        if len(self.X) != len(self.Y):
            raise ValueError("The size does not match X and Y")

        degree = 5  # Задаем степень полинома

        overlap = int(0.1 * len(self.X))  # 10% перекрытия

        # Формируем список сегментов с перекрытием
        segments = [
            (
                self.X[max(0, self._borders[i] - overlap) : min(len(self.X), self._borders[i + 1] + overlap)],
                self.Y[max(0, self._borders[i] - overlap) : min(len(self.Y), self._borders[i + 1] + overlap)],
                self.start_parameter[
                    max(0, self._borders[i] - overlap) : min(len(self.start_parameter), self._borders[i + 1] + overlap)
                ],
            )
            for i in range(len(self._borders) - 1)
        ]

        # Обучаем модели для каждого сегмента
        for x_segment, y_segment, start_segment in segments:
            x_combined = np.column_stack((x_segment, start_segment))
            polynomial_reg, polynomial_features = self._polynomial_regression_two_vars(x_combined, y_segment, degree)
            self.list_polynomial_regression.append(polynomial_reg)
            self.list_polynomial_features.append(polynomial_features)

    def predict_value(self, x: float, start_point: float) -> float:
        """Predicts the value of y based on x and the starting parameter.

        :Args:
            x (float): x value
            start_point (float): start parameter

        Returns:
            float: predicted value of y
        """
        if not (self._left_border <= x <= self._right_border):
            raise ValueError("x is out of range")

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

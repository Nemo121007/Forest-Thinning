import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression


class Line:
    def __init__(self,
                 polynomial_features: PolynomialFeatures = None,
                 polynomial_regression: LinearRegression = None,
                 name: str = None,
                 X: list = None,
                 Y: list = None,
                 start_parameter: float = None):
        # Инициализация атрибутов экземпляра
        self.polynomial_features = polynomial_features or PolynomialFeatures()
        self.polynomial_regression = polynomial_regression or LinearRegression()
        self.name = name
        self.X = np.array(X)
        self.Y = np.array(Y)
        self.start_parameter = start_parameter

    def load_data(self,
                  polynomial_features: PolynomialFeatures = None,
                  polynomial_regression: LinearRegression = None,
                  name: str = None,
                  X: list = None,
                  Y: list = None,
                  start_parameter: float = None):
        """
        Метод для загрузки данных в экземпляр класса Line.
        """
        if polynomial_features is not None:
            self.polynomial_features = polynomial_features
        if polynomial_regression is not None:
            self.polynomial_regression = polynomial_regression
        if name is not None:
            self.name = name
        if X is not None:
            self.X = np.array(X)
        if Y is not None:
            self.Y = np.array(Y)
        if start_parameter is not None:
            self.start_parameter = start_parameter

    @staticmethod
    def _polynomial_regression_two_vars(X, y, degree):
        """Полиномиальная регрессия от двух переменных заданной степени"""
        # Создаем полиномиальные признаки для двух переменных
        polynomial_features = PolynomialFeatures(degree=degree)
        X_polynomial = polynomial_features.fit_transform(X)

        # Линейная регрессия на полиномиальных признаках
        polynomial_reg = LinearRegression()
        polynomial_reg.fit(X_polynomial, y)

        return polynomial_reg, polynomial_features

    def fit_regression(self):
        if not self.start_parameter:
            raise ValueError('Incorrect value start_parameter')
        if not self.X:
            raise ValueError('Incorrect value X')
        if not self.Y:
            raise ValueError('Incorrect value Y')
        if len(self.X) != len(self.Y):
            raise ValueError('The size does not match X and Y')

        start_parameter = [self.start_parameter] * len(self.X)

        # Конвертируем в numpy массивы для модели
        x = np.column_stack((self.X, start_parameter))
        y = np.array(self.Y)

        # Обучаем общую модель на основе всех данных
        degree = 4  # Задаем степень полинома
        self.polynomial_regression, self.polynomial_features = self._polynomial_regression_two_vars(x, y, degree)

    def predict_value(self, x: float, start_point: float):
        x = np.column_stack((x, start_point))
        x_polynomial = self.polynomial_features.transform(x)
        x = self.polynomial_regression.predict(x_polynomial)
        return x

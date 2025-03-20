"""Module for working with a line."""

import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

from app.background_information.Type_line import Type_line


class Line:
    """Class containing the data and methods for working with a line.

    Attributes:
        polynomial_features (PolynomialFeatures): Single polynomial features object
        polynomial_regression (LinearRegression): Single polynomial regression model
        name (str): name of line
        X (np.ndarray): array of x values
        Y (np.ndarray): array of y values
        start_parameter (np.ndarray): array of start parameters
        _left_border (float): left border
        _right_border (float): right border
    """

    def __init__(
        self,
        polynomial_features: PolynomialFeatures = None,
        polynomial_regression: LinearRegression = None,
        name: str = None,
        type_line: Type_line = None,
    ):
        """Initialize the line.

        Args:
            polynomial_features (PolynomialFeatures): Single polynomial features object
            polynomial_regression (LinearRegression): Single polynomial regression model
            name (str): name of line
            type_line (Type_line): type of line

        Returns:
            None
        """
        self.polynomial_features = polynomial_features or PolynomialFeatures(degree=5)  # Default degree
        self.polynomial_regression = polynomial_regression or LinearRegression()
        self.name = name
        self.type_line: Type_line = type_line
        self.X: np.ndarray = np.array([])
        self.Y: np.ndarray = np.array([])
        self.start_parameter: np.ndarray = np.array([])

    def load_info(
        self,
        polynomial_features: PolynomialFeatures = None,
        polynomial_regression: LinearRegression = None,
        name: str = None,
        type_line: Type_line = None,
    ):
        """Load the information for the line.

        Args:
            polynomial_features (PolynomialFeatures): Single polynomial features object
            polynomial_regression (LinearRegression): Single polynomial regression model
            name (str): name of line
            type_line (Type_line): type of line

        Returns:
            None
        """
        if polynomial_features is not None:
            self.polynomial_features = polynomial_features
        if polynomial_regression is not None:
            self.polynomial_regression = polynomial_regression
        if type_line is not None:
            self.name = name
        if type_line is not None:
            self.type_line = type_line

    def append_data(self, X: list[float], Y: list[float]):
        """Append data to the line.

        Args:
            X (list[float]): x values
            Y (list[float]): y values

        Returns:
            None
        """
        if (X is not None) or (Y is not None):
            if (X is None) or (Y is None):
                raise ValueError("X, Y, and start_parameter must all be provided")
            elif len(X) != len(Y):
                raise ValueError("Incorrect len X or Y")

        if self.type_line is None:
            raise ValueError("type_line is None. Set type_line")

        add_x = np.array(X)
        add_y = np.array(Y)

        if self.type_line == Type_line.GROWTH_LINE:
            start_parameter = add_y[0]
        elif self.type_line == Type_line.RECOVERY_LINE:
            start_parameter = add_x[0]
        else:
            start_parameter = 0

        add_start_parameter = np.full(len(add_x), start_parameter)

        self.X = np.concatenate((self.X, add_x))
        self.Y = np.concatenate((self.Y, add_y))
        self.start_parameter = np.concatenate((self.start_parameter, add_start_parameter))

    def fit_regression(self):
        """Fit a single regression model to all data."""
        if self.start_parameter is None or len(self.start_parameter) == 0:
            raise ValueError("Incorrect value start_parameter")
        if self.X is None or len(self.X) == 0:
            raise ValueError("Incorrect value X")
        if self.Y is None or len(self.Y) == 0:
            raise ValueError("Incorrect value Y")
        if len(self.X) != len(self.Y):
            raise ValueError("The size does not match X and Y")

        # Combine X and start_parameter as features
        X_combined = np.column_stack((self.X, self.start_parameter))

        # Transform features to polynomial form
        X_poly = self.polynomial_features.fit_transform(X_combined)

        # Fit the single regression model
        self.polynomial_regression.fit(X_poly, self.Y)

    def predict_value(self, x: float, start_point: float) -> float:
        """Predict the value of the line at a given x value.

        Args:
            x (float): x value
            start_point (float): start point

        Returns:
            float: y value
        """
        # Combine input x and start_point
        combined_x = np.array([[x, start_point]])

        # Transform to polynomial features
        x_poly = self.polynomial_features.transform(combined_x)

        # Predict using the single model
        y = self.polynomial_regression.predict(x_poly)
        return float(y[0])

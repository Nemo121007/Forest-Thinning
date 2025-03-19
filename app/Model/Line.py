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
        X: list = None,
        Y: list = None,
        start_parameter: list[float] = None,
        left_border: float = None,
        right_border: float = None,
    ):
        """Initialization of the Line class."""
        if (X is not None) or (Y is not None) or (start_parameter is not None):
            if (X is None) or (Y is None) or (start_parameter is None):
                raise ValueError("X, Y, and start_parameter must all be provided")
            elif len(X) != len(Y):
                raise ValueError("Incorrect len X or Y")

        self.polynomial_features = polynomial_features or PolynomialFeatures(degree=5)  # Default degree
        self.polynomial_regression = polynomial_regression or LinearRegression()
        self.name = name
        self.type_line: Type_line = type_line
        self.X: np.ndarray = np.array(X) if X else None
        self.Y: np.ndarray = np.array(Y) if Y else None
        if X is not None and start_parameter is not None and left_border is not None and right_border is not None:
            self.start_parameter: np.ndarray = np.array([start_parameter] * len(X))
            self.left_border = X[0]
            self.right_border = X[-1]

    def load_data(
        self,
        polynomial_features: PolynomialFeatures = None,
        polynomial_regression: LinearRegression = None,
        name: str = None,
        type_line: Type_line = None,
        X: list[float] = None,
        Y: list[float] = None,
        start_parameter: float = None,
    ):
        """Load data into the Line class."""
        if (X is not None) or (Y is not None) or (start_parameter is not None):
            if (X is None) or (Y is None) or (start_parameter is None):
                raise ValueError("X, Y, and start_parameter must all be provided")
            elif len(X) != len(Y):
                raise ValueError("Incorrect len X or Y")

        if polynomial_features is not None:
            self.polynomial_features = polynomial_features
        if polynomial_regression is not None:
            self.polynomial_regression = polynomial_regression
        if type_line is not None:
            self.name = name
        if type_line is not None:
            self.type_line = type_line
        if X is not None:
            self.X = np.array(X)
            self.left_border = X[0]
            self.right_border = X[-1]
        if Y is not None:
            self.Y = np.array(Y)
        if (start_parameter is not None) and (X is not None):
            self.start_parameter = np.array([start_parameter] * len(X))

    def append_data(self, X: list[float], Y: list[float], start_parameter: float):
        """Add new data to current arrays X, Y, and start_parameter."""
        if (X is None) or (Y is None) or (start_parameter is None):
            raise ValueError("X, Y, and start_parameter must all be provided")
        elif len(X) != len(Y):
            raise ValueError("Incorrect len X or Y")

        x = np.array(X)
        y = np.array(Y)
        new_start_parameter = np.full(len(x), start_parameter)

        if self.X is None:
            self.X = x
            self.Y = y
            self.start_parameter = new_start_parameter
        else:
            self.X = np.concatenate((self.X, x))
            self.Y = np.concatenate((self.Y, y))
            self.start_parameter = np.concatenate((self.start_parameter, new_start_parameter))

        # Sort by X
        sorted_indices = np.argsort(self.X)
        self.X = self.X[sorted_indices]
        self.Y = self.Y[sorted_indices]
        self.start_parameter = self.start_parameter[sorted_indices]

        # Update borders
        self.left_border = float(self.X[0])
        self.right_border = float(self.X[-1])

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
        """Predicts the value of y based on x and the starting parameter."""
        # Combine input x and start_point
        combined_x = np.array([[x, start_point]])

        # Transform to polynomial features
        x_poly = self.polynomial_features.transform(combined_x)

        # Predict using the single model
        y = self.polynomial_regression.predict(x_poly)
        return float(y[0])

    # def save_model(self) -> dict:
    #     """Save model to a file (placeholder).

    #     Arg:
    #         None

    #     Returns:
    #         dict: Dictionary containing the name of the model and the names of the saved files
    #     """
    #     path_polynomial_features = Paths.MODEL_DIRECTORY_MODELS / f"{self.name}_polynomial_features.pkl"
    #     path_polynomial_regression = Paths.MODEL_DIRECTORY_MODELS / f"{self.name}_polynomial_regression.pkl"

    #     answer_dict = {
    #         "name": self.name,
    #         "polynomial_features": f"{self.name}_polynomial_features.pkl",
    #         "polynomial_regression": f"{self.name}_polynomial_regression.pkl",
    #         "left_border": self._left_border,
    #         "right_border": self._right_border,
    #     }

    #     self.polynomial_features.save(path_polynomial_features)
    #     self.polynomial_regression.save(path_polynomial_regression)
    #     return answer_dict

    # def load_model(self, name: str):
    #     """Load model from a file (placeholder)."""
    #     path_polynomial_features = Paths.MODEL_DIRECTORY_MODELS / f"{name}_polynomial_features.pkl"
    #     path_polynomial_regression = Paths.MODEL_DIRECTORY_MODELS / f"{name}_polynomial_regression.pkl"

    #     self.polynomial_features.load(path_polynomial_features)
    #     self.polynomial_regression.load(path_polynomial_regression)

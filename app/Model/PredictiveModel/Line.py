"""Module for modeling and predicting lines using polynomial regression.

This module provides the Line class, which manages data for a specific line type (e.g., growth,
logging) and uses polynomial regression to fit and predict values based on input data.
"""

import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from ...background_information.Type_line import Type_line
from ...background_information.Settings import Settings


class Line:
    """A class for modeling and predicting lines using polynomial regression.

    Handles data storage, fitting, and prediction for a specific line type, using polynomial
    features and linear regression. Supports growth, recovery, and other line types defined
    by Type_line, with configurable approximation degree from Settings.

    Attributes:
        polynomial_features (PolynomialFeatures): The polynomial feature transformer.
        polynomial_regression (LinearRegression): The linear regression model for predictions.
        type_line (Type_line): The type of line (e.g., growth, logging).
        X (np.ndarray): Array of x-values for training data.
        Y (np.ndarray): Array of y-values for training data.
        start_parameter (np.ndarray): Array of starting parameters for training data.
    """

    def __init__(
        self,
        polynomial_features: PolynomialFeatures = None,
        polynomial_regression: LinearRegression = None,
        type_line: Type_line = None,
    ):
        """Initialize the Line model.

        Sets up the polynomial feature transformer, regression model, and line type, with
        defaults for polynomial degree from Settings.

        Args:
            polynomial_features (PolynomialFeatures, optional): Custom polynomial feature transformer. Defaults to None.
            polynomial_regression (LinearRegression, optional): Custom linear regression model. Defaults to None.
            type_line (Type_line, optional): The type of line to model. Defaults to None.

        Returns:
            None
        """
        # TODO: Настроить степень аппроксимации
        self.polynomial_features = polynomial_features or PolynomialFeatures(degree=Settings.DEGREE_APPROXIMATION)
        self.polynomial_regression = polynomial_regression or LinearRegression()
        self.type_line: Type_line = type_line
        self.X: np.ndarray = np.array([])
        self.Y: np.ndarray = np.array([])
        self.start_parameter: np.ndarray = np.array([])

    def load_info(
        self,
        polynomial_features: PolynomialFeatures = None,
        polynomial_regression: LinearRegression = None,
        type_line: Type_line = None,
    ):
        """Update the model configuration with new parameters.

        Replaces existing polynomial features, regression model, or line type if provided.

        Args:
            polynomial_features (PolynomialFeatures, optional): New polynomial feature transformer. Defaults to None.
            polynomial_regression (LinearRegression, optional): New linear regression model. Defaults to None.
            type_line (Type_line, optional): New line type. Defaults to None.

        Returns:
            None
        """
        if polynomial_features is not None:
            self.polynomial_features = polynomial_features
        if polynomial_regression is not None:
            self.polynomial_regression = polynomial_regression
        if type_line is not None:
            self.type_line = type_line

    def append_data(self, X: list[float], Y: list[float]):
        """Append training data to the model.

        Adds x and y data points, assigns a start parameter based on the line type, and
        validates input consistency.

        Args:
            X (list[float]): List of x-values to append.
            Y (list[float]): List of y-values to append.

        Returns:
            None

        Raises:
            ValueError: If X or Y is None, lengths mismatch, or type_line is not set.
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

    def clear_train_data(self):
        """Clear all training data from the model.

        Resets the x-values, y-values, and start parameters to empty arrays.

        Returns:
            None
        """
        self.X = np.array([])
        self.Y = np.array([])
        self.start_parameter = np.array([])

    def fit_regression(self):
        """Fit the polynomial regression model to the training data.

        Combines x-values and start parameters as features, transforms them to polynomial
        form, and fits the regression model.

        Returns:
            None

        Raises:
            ValueError: If X, Y, or start_parameter is empty or lengths mismatch.
        """
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
        """Predict a single y-value for a given x and start point.

        Uses the fitted model to compute the prediction based on polynomial features.

        Args:
            x (float): The x-value for prediction.
            start_point (float): The starting parameter for the prediction.

        Returns:
            float: The predicted y-value.
        """
        # Combine input x and start_point
        combined_x = np.array([[x, start_point]])

        # Transform to polynomial features
        x_poly = self.polynomial_features.transform(combined_x)

        # Predict using the single model
        y = self.polynomial_regression.predict(x_poly)
        return float(y[0])

    def predict_list_value(self, list_x: list[float], start_point: float) -> list[float]:
        """Predict y-values for a list of x-values and a start point.

        Uses the fitted model to compute predictions for multiple x-values.

        Args:
            list_x (list[float]): List of x-values for prediction.
            start_point (float): The starting parameter for the predictions.

        Returns:
            list[float]: List of predicted y-values.
        """
        combined_x = np.array([[x, start_point] for x in list_x])
        x_poly = self.polynomial_features.transform(combined_x)
        y = self.polynomial_regression.predict(x_poly)
        return y.tolist()

    def predict_line(
        self, start_x: float, end_x: float, step: float, start_point: float
    ) -> tuple[list[float], list[float]]:
        """Generate x and y values for a line over a range of x-values.

        Creates a sequence of x-values from start_x to end_x with the given step, and
        predicts corresponding y-values using the fitted model.

        Args:
            start_x (float): The starting x-value for the range.
            end_x (float): The ending x-value for the range.
            step (float): The step size between x-values.
            start_point (float): The starting parameter for the predictions.

        Returns:
            tuple[list[float], list[float]]: A tuple of (x_values, y_values) for the predicted line.
        """
        x_values = np.arange(start_x, end_x + step, step)

        combined_x = np.array([[x, start_point] for x in x_values])
        x_poly = self.polynomial_features.transform(combined_x)
        y = self.polynomial_regression.predict(x_poly)
        return x_values.tolist(), y.tolist()

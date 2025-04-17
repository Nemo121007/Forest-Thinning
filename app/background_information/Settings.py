"""Module for defining configuration settings in a reference data system.

This module provides the Settings class, a dataclass that stores constants for
graph plotting and approximation used throughout the application.
"""

from dataclasses import dataclass


@dataclass
class Settings:
    """A dataclass for storing configuration settings for graph plotting and approximation.

    Defines constants used in the application for controlling the degree of polynomial
    approximation and the step size for plotting graphics.

    Attributes:
        DEGREE_APPROXIMATION (int): The degree of polynomial approximation for models, defaults to 5.
        STEP_PLOTTING_GRAPH (float): The step size for generating graph points, defaults to 0.5.
    """

    DEGREE_APPROXIMATION: int = 5

    STEP_PLOTTING_GRAPH: int = 0.5

    INCREASE_GRAPHIC: float = 0.01

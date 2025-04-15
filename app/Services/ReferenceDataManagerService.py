"""Module for managing singleton access to ReferenceDataManager.

This module provides a singleton decorator and the ReferenceDataManagerServices class,
which ensures a single instance of ReferenceDataManager is used throughout the application.
"""

from typing import Any, TypeVar
from collections.abc import Callable
from ..Model.ReferenceData.ReferenceDataManager import ReferenceDataManager
from ..Model.PredictiveModel.Graph import Graph

# Define a generic type for the class
T = TypeVar("T")


def singleton(cls: type[T]) -> Callable[..., T]:
    """A decorator to enforce the singleton pattern for a class.

    Ensures that only one instance of the decorated class is created, reusing it for
    subsequent calls. Stores instances in a dictionary keyed by class.

    Args:
        cls: The class to be decorated.

    Returns:
        Callable[..., T]: A function that returns the singleton instance of the class.
    """
    instances: dict[type[T], T] = {}

    def get_instance(*args: Any, **kwargs: Any) -> T:
        """Create or return the singleton instance of the class.

        Args:
            *args: Positional arguments to pass to the class constructor.
            **kwargs: Keyword arguments to pass to the class constructor.

        Returns:
            T: The singleton instance of the class.
        """
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class ReferenceDataManagerServices:
    """A singleton class for accessing the ReferenceDataManager.

    Provides a single point of access to a ReferenceDataManager instance, ensuring only
    one instance is used across the application.

    Attributes:
        manager (ReferenceDataManager): The singleton instance of ReferenceDataManager.
    """

    def __init__(self) -> None:
        """Initialize the ReferenceDataManagerServices with a ReferenceDataManager instance.

        Returns:
            None
        """
        self.manager = ReferenceDataManager()
        self.predict_model = Graph()

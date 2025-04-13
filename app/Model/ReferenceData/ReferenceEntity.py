"""Module for defining an abstract base class for reference entities.

This module provides the ReferenceEntity abstract base class, which serves as a foundation
for managing reference data with transactional support. It includes methods for data
manipulation, usage tracking, and persistence, using a dictionary-based storage mechanism.
"""

from abc import ABC, abstractmethod
from contextlib import contextmanager


class ReferenceEntity(ABC):
    """An abstract base class for managing reference entities.

    Provides a framework for storing and manipulating reference data with transactional
    support. Subclasses must implement initialization and data persistence logic. Tracks
    data usage and supports querying of data lists and usage status.

    Attributes:
        _data (dict): Dictionary storing reference data, keyed by name.
        _used (dict): Dictionary tracking usage status of reference items.
        _data_key (str): Key used to identify the data dictionary in transactions.
        _current_data (dict, optional): Temporary data state during transactions.
    """

    def __init__(self, data_key: str):
        """Initialize the ReferenceEntity with a data key.

        Sets up internal storage for data, usage tracking, and transaction management.

        Args:
            data_key (str): The key used to identify the data dictionary in transactions.
        """
        self._data = {}
        self._used = {}
        self._data_key = data_key
        self._current_data = None

    @contextmanager
    def transaction(self) -> None:
        """Provide a transactional context for data modifications.

        Creates a snapshot of the current data state, yields control to the caller, and
        restores the snapshot on failure. Clears the snapshot on completion.

        Yields:
            None

        Raises:
            Exception: Propagates any exception raised within the transaction, after
                restoring the original data state.
        """
        self._current_data = {self._data_key: dict(self._data)}
        try:
            yield
        except Exception as e:
            if self._current_data:
                self.initialize(self._current_data)
            raise e
        finally:
            self._current_data = None

    @abstractmethod
    def initialize(self, data: dict) -> None:
        """Initialize the entity with provided data.

        Subclasses must implement this method to load data into the internal storage.

        Args:
            data (dict): The data to initialize the entity, typically containing a
                dictionary under the key specified by _data_key.

        Returns:
            None
        """
        pass

    @abstractmethod
    def save_data(self, reference_data: dict) -> None:
        """Save the provided reference data.

        Subclasses must implement this method to persist the reference data.

        Args:
            reference_data (dict): The data to be saved.

        Returns:
            None
        """
        pass

    def get_list(self) -> list:
        """Retrieve a list of reference item names.

        Returns:
            list: A list of keys (names) from the internal data dictionary.
        """
        return list(self._data.keys())

    def get_list_used(self) -> list[tuple[str, bool]]:
        """Retrieve a list of reference items with their usage status.

        Returns:
            list[tuple[str, bool]]: A list of tuples, each containing an item name and
                its usage status (True if used, False otherwise).
        """
        return [(key, self._used[key]) for key in self._data.keys()]

    def check_used(self, name: str) -> bool:
        """Check if a reference item is used.

        Args:
            name (str): The name of the item to check.

        Returns:
            bool: True if the item is marked as used, False otherwise.
        """
        return self._used.get(name, False)

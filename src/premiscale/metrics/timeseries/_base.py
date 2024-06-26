"""
ABCs for metrics storage methods.
"""


from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from typing import Any, Dict, Tuple


log = logging.getLogger(__name__)


class TimeSeries(ABC):
    """
    An abstract base class with a skeleton interface for metrics class-types.
    """

    @abstractmethod
    def open(self) -> None:
        """
        Open a connection to the metrics backend these methods interact with.

        Raises:
            NotImplementedError: if the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """
        Close the connection to the metrics backend.

        Raises:
            NotImplementedError: if the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        """
        Commit any changes to the database.

        Raises:
            NotImplementedError: if the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def insert(self, data: Dict) -> None:
        """
        Insert a point into the metrics store.

        Args:
            data (Dict): the data to insert.

        Raises:
            NotImplementedError: if the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def insert_batch(self, data: Tuple[Dict]) -> None:
        """
        Insert a batch of points into the metrics store.

        Args:
            data (Tuple[Dict]): the data to insert.

        Raises:
            NotImplementedError: if the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """
        Clear the metrics store of all data.

        Raises:
            NotImplementedError: if the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def _run_retention_policy(self) -> None:
        """
        Run the retention policy on the database, removing points older than the retention policy.

        Raises:
            NotImplementedError: if the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> Tuple:
        """
        Get all the data in the metrics store.

        Returns:
            Tuple: all the data in the metrics store.

        Raises:
            NotImplementedError: if the method is not implemented.
        """
        raise NotImplementedError

    def __enter__(self) -> TimeSeries:
        self.open()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
        return
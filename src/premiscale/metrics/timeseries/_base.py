"""
ABCs for metrics storage methods.
"""


from __future__ import annotations

import logging

from typing import Any
from abc import ABC


log = logging.getLogger(__name__)


class TimeSeries(ABC):
    """
    An abstract base class with a skeleton interface for metrics class-types.
    """

    def open(self) -> None:
        """
        Open a connection to the metrics backend these methods interact with.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def close(self) -> None:
        """
        Close the connection to the metrics backend.

        This method should also dereference any secrets that may be stored in memory.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def commit(self) -> None:
        """
        Commit any changes to the database.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def __enter__(self) -> TimeSeries:
        self.open()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
        return
"""
Methods for interacting with an in-memory metrics store.
"""


from __future__ import annotations

from typing import TYPE_CHECKING
from premiscale.metrics.timeseries._base import TimeSeries
from tinyflux import TinyFlux, Point, FieldQuery, TagQuery, TimeQuery

if TYPE_CHECKING:
    from premiscale.config.v1alpha1 import Config


class Local(TimeSeries):
    """
    Implement required interface methods for storing host metrics in memory.
    """
    def __init__(self, config: Config) -> None:
        self.config = config

    def open(self) -> None:
        """
        Open a connection to the metrics backend these methods interact with.
        """
        pass

    def close(self) -> None:
        """
        Close the connection to the metrics backend.

        This method should also dereference any secrets that may be stored in memory.
        """
        pass

    def commit(self) -> None:
        """
        Commit any changes to the database.
        """
        pass
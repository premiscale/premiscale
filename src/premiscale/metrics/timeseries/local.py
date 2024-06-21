"""
Methods for interacting with an in-memory metrics store.
"""


from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from datetime import timedelta, datetime, timezone
from tinyflux import TinyFlux, Point, FieldQuery, TagQuery, TimeQuery
from tinyflux.storages import MemoryStorage, CSVStorage
from premiscale.metrics.timeseries._base import TimeSeries

if TYPE_CHECKING:
    from typing import Dict, List


log = logging.getLogger(__name__)


class Local(TimeSeries):
    """
    Implement an interface to storing host metrics in memory.
    """

    def __init__(self, retention: timedelta, file: str | None = None) -> None:
        self.retention: timedelta = retention
        self._connection: TinyFlux
        self.file = file

    def open(self) -> None:
        """
        Open a connection to the metrics backend these methods interact with.
        """
        if self.file is not None:
            self._connection = TinyFlux(
                path=self.file,
                storage=CSVStorage
            )
        else:
            self._connection = TinyFlux(
                storage=MemoryStorage
            )

    def close(self) -> None:
        """
        Close the connection to the metrics backend.
        """
        self._connection.close()

    def commit(self) -> None:
        """
        Commit any changes to the database. In this class' case, we do nothing since everything is committed by default.
        """
        return None

    def insert(self, data: Dict) -> None:
        """
        Insert a point into the metrics store.
        """
        point = Point(data)

        self._connection.insert(point)
        self._run_retention_policy()

    def insert_batch(self, data: Dict) -> None:
        """
        Insert a batch of points into the metrics store.
        """
        points = [Point(d) for d in data.get('data', [])]

        self._connection.insert_multiple(points)
        self._run_retention_policy()

    def clear(self) -> None:
        """
        Clear the metrics store of all data.
        """
        self._connection.remove_all()

    def _run_retention_policy(self) -> None:
        """
        Run the retention policy on the database, removing points older than the retention policy.
        """
        timeq = TimeQuery()
        time_now = datetime.now(timezone.utc) - self.retention
        self._connection.remove(timeq < time_now)
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
    from tinyflux.queries import Query
    from typing import Dict, Tuple


log = logging.getLogger(__name__)


class Local(TimeSeries):
    """
    Implement an interface to storing host metrics in memory.
    """

    # # https://medium.com/analytics-vidhya/how-to-create-a-thread-safe-singleton-class-in-python-822e1170a7f6
    # _instance = None
    # # _lock = threading.Lock()
    # def __new__(cls):
    #     if cls._instance is None:
    #         # with cls._lock:
    #         if not cls._instance:
    #             cls._instance = super().__new__(cls)
    #     return cls._instance

    def __init__(self, retention: timedelta, file: str | None = None) -> None:
        self.retention: timedelta = retention
        self._connection: TinyFlux
        self.file = file

    def is_connected(self) -> bool:
        """
        Check if the connection to the MySQL database is open.

        Returns:
            bool: True if the connection is open.
        """
        return self._connection is not None

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
        Commit any changes to the database. In this class' case, we do nothing since everything is
        committed by default.
        """
        return None

    def insert(self, data: Dict) -> None:
        """
        Insert a point into the metrics store.

        Args:
            data (Dict): a dictionary containing the data to insert.
        """
        point = Point(**data)

        self._connection.insert(point)
        self._run_retention_policy()

    def insert_batch(self, data: Tuple) -> None:
        """
        Insert a batch of points into the metrics store.

        Args:
            data (Tuple): a tuple of dictionaries containing the data to insert.
        """

        # https://tinyflux.readthedocs.io/en/latest/preparing-data.html
        # This field requires 4 arguments: measurement, time, tags, and fields.
        points = [Point(**datum) for datum in data]

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
        removed_item_number = 0

        for measurement in ['cpu', 'memory', 'block', 'net']:
            removed_item_number += self._connection.remove(
                TimeQuery() < datetime.now(tz=timezone.utc) - self.retention,
                measurement=measurement
            )

        log.debug(f"Retention removed {removed_item_number} items from the database.")

    def get_all(self, measurement: str | None = None) -> Tuple:
        """
        Get all the data in the metrics store.

        Args:
            measurement (str | None): the measurement to get data for. If None, all data is returned. (Default: None.)

        Returns:
            Tuple: all the data in the metrics store.
        """
        return self._connection.search(
            TimeQuery() > (datetime.now(timezone.utc) - self.retention),
            measurement=measurement,
            sorted=True
        )
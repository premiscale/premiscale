"""
Methods for interacting with influxdb.
"""


from __future__ import annotations

import influxdb

from typing import TYPE_CHECKING
from premiscale.metrics.timeseries._base import TimeSeries

if TYPE_CHECKING:
    from typing import Dict


class InfluxDB(TimeSeries):
    """
    Implement required interface methods that connect with InfluxDB.
    """
    def __init__(self, url: str, database: str, username: str, password: str) -> None:
        self.url = url
        self.database = database
        self._connection = influxdb.InfluxDBClient(
            self.url,
            self.database,
            username,
            password
        )

    def open(self) -> None:
        """
        Open a connection to the metrics backend these methods interact with.
        """
        raise NotImplementedError

    def close(self) -> None:
        """
        Close the connection to the metrics backend.
        """
        raise NotImplementedError

    def commit(self) -> None:
        """
        Commit any changes to the database.
        """
        raise NotImplementedError

    def insert(self, data: Dict) -> None:
        """
        Insert a point into the metrics store.
        """
        raise NotImplementedError

    def insert_batch(self, data: Dict) -> None:
        """
        Insert a batch of points into the metrics store.
        """
        raise NotImplementedError

    def clear(self) -> None:
        """
        Clear the metrics store of all data.
        """
        raise NotImplementedError

    def _run_retention_policy(self) -> None:
        """
        Run the retention policy on the database, removing points older than the retention policy.
        """
        raise NotImplementedError
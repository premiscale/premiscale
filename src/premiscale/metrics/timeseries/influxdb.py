"""
Methods for interacting with influxdb.
"""


from __future__ import annotations

import logging
import sys

from typing import TYPE_CHECKING
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from premiscale.metrics.timeseries._base import TimeSeries

if TYPE_CHECKING:
    from typing import Dict, Tuple
    from influxdb_client import QueryApi, WriteApi, DeleteApi
    from premiscale.config.v1alpha1 import TimeSeries as TimeSeriesConfig


log = logging.getLogger(__name__)


class InfluxDB(TimeSeries):
    """
    Implement required interface methods that connect with InfluxDB.
    """
    def __init__(self, time_series_config: TimeSeriesConfig) -> None:
        if time_series_config.connection is None:
            log.error("InfluxDB connection information must be provided in the configuration file")
            sys.exit(1)

        # Unpack objects in the TimeSeries-dataclass.
        self.url = time_series_config.connection.url

        # This is analogous to the bucket name in InfluxDB.
        self.bucket = time_series_config.connection.database

        # Credentials
        self._username = time_series_config.connection.credentials.username
        self._password = time_series_config.connection.credentials.password

        # Connection
        self._connection: InfluxDBClient | None = None

        # APIs
        self._write_api: WriteApi | None = None
        self._query_api: QueryApi | None = None
        self._delete_api: DeleteApi | None = None

        # Retention policy
        self.trailing = time_series_config.trailing

    def is_connected(self) -> bool:
        """
        Indicate whether or not the connection to the metrics backend is open.

        Returns:
            bool: True if the connection is open, False otherwise.
        """
        return self._connection is not None

    def open(self) -> None:
        """
        Open a connection to the metrics backend these methods interact with.
        """
        log.debug(f'Opening connection to InfluxDB at "{self.url}".')
        self._connection = InfluxDBClient(
            self.url,
            self.bucket,
            self._username,
            self._password
        )
        log.debug(f'Connection to InfluxDB at "{self.url}" opened.')

        self._query_api = self._connection.query_api()
        self._write_api = self._connection.write_api(
            write_options=SYNCHRONOUS
        )
        self._delete_api = self._connection.delete_api()

    def close(self) -> None:
        """
        Close the connection to the metrics backend.
        """
        log.debug("Closing connection to InfluxDB.")
        if self._connection is not None:
            self._connection.close()
        self._query_api = None
        self._write_api = None
        self._delete_api = None

    def get_all(self) -> Tuple:
        """
        Get all the data in the metrics store.

        Returns:
            Tuple: all the data in the metrics store. If the connection is not open, return an empty tuple.
        """
        if self._query_api is None:
            log.error("InfluxDB connection is not open.")
            return tuple()

        data = self._query_api.query(
            f'from(bucket: "{self.bucket}") |> range(start: -{self.trailing}s)'
        )

        return data

    def commit(self) -> None:
        """
        Commit any changes to the database. By default, this does nothing, since InfluxDB isn't transactional.
        """
        log.warning("InfluxDB is not transactional, so committing does nothing.")
        return None

    def insert(self, datum: Dict) -> None:
        """
        Insert a point into the metrics store.

        Args:
            datum (Dict): the data to insert.
        """
        if self._write_api is None:
            log.error("InfluxDB connection is not open.")
            return None

        point = Point(**datum)

        self._write_api.write(
            bucket=self.bucket,
            record=point
        )
        self._run_retention_policy()

    def insert_batch(self, data: Tuple) -> None:
        """
        Insert a batch of points into the metrics store.

        Args:
            data (Tuple): the data to insert.

        Raises:
            NotImplementedError: if the method is not implemented.
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

        Raises:
            NotImplementedError: if the method is not implemented.
        """
        raise NotImplementedError
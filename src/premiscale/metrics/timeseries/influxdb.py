"""
Methods for interacting with influxdb.
"""


from __future__ import annotations

import logging
import sys

from typing import TYPE_CHECKING
from influxdb_client import InfluxDBClient, Point, WritePrecision, BucketRetentionRules
from influxdb_client.client.write_api import SYNCHRONOUS
from premiscale.metrics.timeseries._base import TimeSeries

if TYPE_CHECKING:
    from typing import Dict, Tuple
    from influxdb_client import (
        QueryApi,
        WriteApi,
        DeleteApi,
        BucketsAPI
    )
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

        # database is analogous to the bucket name in InfluxDB.
        self.bucket = time_series_config.connection.database

        self.organization = time_series_config.connection.organization

        # Credentials
        self._username = time_series_config.connection.credentials.username # this isn't used for InfluxDB
        self._password = time_series_config.connection.credentials.password # this field is analogous to the connection token

        # Connection
        self._connection: InfluxDBClient | None = None

        # APIs
        self._write_api: WriteApi | None = None
        self._query_api: QueryApi | None = None
        self._delete_api: DeleteApi | None = None
        self._buckets_api: BucketsAPI | None = None

        # Retention policy
        self.retention = time_series_config.retention

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
        log.debug(f'Opening connection to InfluxDB at "{self.url}"')

        self._connection = InfluxDBClient(
            url=self.url,
            token=self._password,
            org=self.organization
        )

        log.debug(f'Connection to InfluxDB at "{self.url}" opened')

        self._buckets_api = self._connection.buckets_api()
        self._query_api = self._connection.query_api()
        self._write_api = self._connection.write_api(
            write_options=SYNCHRONOUS
        )
        self._delete_api = self._connection.delete_api()

        # Check to ensure the bucket we wish to write to exists.
        if self._buckets_api.find_bucket_by_name(self.bucket) is None:
            log.debug(f'Creating bucket "{self.bucket}"')
            self._buckets_api.create_bucket(
                bucket_name=self.bucket,
                # https://github.com/influxdata/influxdb-client-python/blob/653af4657265755ff718c2f03339616d036fea3c/influxdb_client/client/bucket_api.py#L31
                retention_rules=BucketRetentionRules(
                    type='expire',
                    every_seconds=self.retention
                )
            )

    def close(self) -> None:
        """
        Close the connection to the metrics backend.
        """
        log.debug("Closing connection to InfluxDB")

        if self._connection is not None:
            self._connection.close()

        self._buckets_api = None
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
            log.error("InfluxDB connection is not open")
            return tuple()

        data = self._query_api.query(
            f'from(bucket: "{self.bucket}") |> range(start: -{self.retention}s)'
        )

        return data

    def commit(self) -> None:
        """
        Commit any changes to the database. By default, this does nothing, since InfluxDB isn't transactional.
        """
        log.warning("InfluxDB is not transactional, so committing does nothing.")

    def insert(self, datum: Dict) -> None:
        """
        Insert a point into the metrics store.

        Args:
            datum (Dict): the data to insert.
        """
        if self._write_api is None:
            log.error("InfluxDB connection is not open.")
            return None

        point = Point.from_dict(
            datum,
            write_precision=WritePrecision.S
        )

        self._write_api.write(
            bucket=self.bucket,
            record=point
        )

    def insert_batch(self, data: Tuple) -> None:
        """
        Insert a batch of points into the metrics store.

        Args:
            data (Tuple): the data to insert.
        """
        if self._write_api is None:
            log.error("InfluxDB connection is not open.")
            return None

        # https://github.com/influxdata/influxdb-client-python/blob/653af4657265755ff718c2f03339616d036fea3c/influxdb_client/client/write/point.py#L81
        points = [
            Point.from_dict(
                datum,
                write_precision=WritePrecision.S
            ) for datum in data
        ]

        for point in points:
            self._write_api.write(
                bucket=self.bucket,
                org=self.organization,
                record=point
            )

    def clear(self) -> None:
        """
        Clear the metrics store of all data.
        """
        if self._delete_api is None:
            log.error("InfluxDB connection is not open.")
            return None

        log.info("Clearing all data from InfluxDB")

        for measurement in ['cpu', 'memory', 'block', 'net']:
            self._delete_api.delete(
                bucket=self.bucket,
                predicate=f'_measurement == "{measurement}"',
                start='1970-01-01T00:00:00Z', # epoch 0
                stop='now()'
            )

    def _run_retention_policy(self) -> None:
        """
        Run the retention policy on the database, removing points older than the retention policy.

        InfluxDB allows us to set a retention interval automatically, so we don't need to manually delete old data.
        """
        log.warning("InfluxDB automatically handles retention policies, so there's no need to call this method manually within this class")

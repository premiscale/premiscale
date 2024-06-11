"""
Methods for interacting with influxdb.
"""

import influxdb

from premiscale.metrics.timeseries._base import TimeSeries


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

    def __call__(self) -> None:
        """
        Connect to the InfluxDB database.
        """
        ...

    def open(self) -> None:
        """
        Open a connection to the metrics backend these methods interact with.
        """
        raise NotImplementedError

    def close(self) -> None:
        """
        Close the connection to the metrics backend.

        This method should also dereference any secrets that may be stored in memory.
        """
        raise NotImplementedError

    def commit(self) -> None:
        """
        Commit any changes to the database.
        """
        raise NotImplementedError
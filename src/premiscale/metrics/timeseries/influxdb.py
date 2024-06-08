"""
Methods for interacting with influxdb.
"""

import influxdb

from premiscale.metrics._base import Metrics


class InfluxDB(Metrics):
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
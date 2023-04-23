"""
Methods for interacting with influxdb.
"""

import influxdb

from premiscale.metrics._base import Metrics


class InfluxDB:
    def __init__(self, url: str, database: str, username: str, password: str) -> None:
        self.url = url
        self.database = database
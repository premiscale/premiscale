"""
Methods for interacting with influxdb.
"""

import influxdb

from src.premiscale.metrics._base import Metrics


class InfluxDB:
    """
    Implement required interface methods that connect with InfluxDB.
    """
    def __init__(self, url: str, database: str, username: str, password: str) -> None:
        self.url = url
        self.database = database
"""
Methods for interacting with influxdb.
"""

import influxdb


class InfluxDB:
    def __init__(self, url: str, database: str, username: str, password: str) -> None:
        self.url = url
        self.database = database
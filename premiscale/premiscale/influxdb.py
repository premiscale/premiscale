"""
Methods for interacting with influxdb.
"""

import influxdb


class InfluxDB:
    def __init__(self, url: str) -> None:
        self.url = url
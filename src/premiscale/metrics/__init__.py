"""
A module for handling metrics collection from hosts.
"""


import logging

from setproctitle import setproctitle
from cattrs import unstructure
from premiscale.metrics._base import Metrics
from premiscale.config.v1alpha1 import Config


log = logging.getLogger(__name__)


def build_metrics(config: Config) -> Metrics:
    """
    Build a metrics collection class instance for storing metrics  hosts. Only one of these loops is created; metrics
    are published to influxdb for retrieval and query by the ASG loop, which evaluates
    on a per-ASG basis whether Actions need to be taken.
    """
    match config.controller.databases.metrics.type:
        case 'memory':
            from premiscale.metrics.local import Local

            return Local(config)
        case 'influxdb':
            from premiscale.metrics.influxdb import InfluxDB

            connection = unstructure(config.controller.databases.metrics.connection)
            del(connection['type'])

            return InfluxDB(**connection)
        case _:
            raise ValueError(f'Unknown metrics type: {config.controller.databases.metrics.type}')
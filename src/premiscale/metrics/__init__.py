"""
A module for handling metrics collection from hosts. This includes time-series and state data.
The distinguishing factor between state and time-series data is where it's sourced from; state
data is sourced from the hosts on which the VMs reside, while time-series data is sourced from
the VMs on the hosts.
"""


import logging

from typing import Iterator, TYPE_CHECKING
from setproctitle import setproctitle
from cattrs import unstructure, structure
from premiscale.config.v1alpha1 import Host


if TYPE_CHECKING:
    from multiprocessing.queues import Queue
    from premiscale.config.v1alpha1 import Config
    from premiscale.metrics.state._base import State
    from premiscale.metrics.timeseries._base import TimeSeries


log = logging.getLogger(__name__)


def build_timeseries_connection(config: Config) -> TimeSeries:
    """
    Build a metrics collection class instance for storing metrics  hosts. Only one of
    these loops is created; metrics are published to influxdb for retrieval and query
    by the ASG loop, which evaluates on a per-ASG basis whether Actions need to be taken.
    """
    match config.controller.databases.timeseries.type:
        case 'memory':
            from premiscale.metrics.timeseries.local import Local

            return Local(config)
        case 'influxdb':
            from premiscale.metrics.timeseries.influxdb import InfluxDB

            connection = unstructure(config.controller.databases.timeseries.connection)
            del(connection['type'])

            return InfluxDB(**connection)
        case _:
            raise ValueError(f'Unknown timeseries database type: {config.controller.databases.timeseries.type}')


def build_state_connection(config: Config) -> State:
    """
    Build a state collection class.
    """
    match config.controller.databases.state.type:
        case 'memory':
            # SQLite
            from premiscale.metrics.state.local import Local

            return Local()
        case 'mysql':
            from premiscale.metrics.state.mysql import MySQL

            connection = unstructure(config.controller.databases.state.connection)
            del(connection['type'])

            return MySQL(**connection)
        case _:
            raise ValueError(f'Unknown state database type: {config.controller.databases.state.type}')


class MetricsCollector:
    """
    Oversee visiting every host and collecting metrics and storing them in the appropriate backend database.
    """
    def __init__(self, config: Config, timeseries_enabled: bool = False) -> None:
        self.timeseriesConnection: TimeSeries | None = None
        self.timeseries_enabled = timeseries_enabled
        self.config = config

    def __call__(self) -> None:
        setproctitle('metrics-collector')
        log.debug('Starting metrics collection subprocess')

        if self.timeseries_enabled:
            log.debug(f'Opening time series database connection.')
            self.timeseriesConnection = build_timeseries_connection(self.config)

        log.debug('Opening state database connection.')
        self.stateConnection = build_state_connection(self.config)

    def hostIterator(self) -> Iterator:
        """
        Create an iterator that visits every host.
        """
        for host in self.config.controller.autoscale.hosts:
            yield structure(host, Host)
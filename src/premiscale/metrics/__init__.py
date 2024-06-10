"""
A module for handling metrics collection from hosts. This includes time-series and state data.
The distinguishing factor between state and time-series data is where it's sourced from; state
data is sourced from the hosts on which the VMs reside, while time-series data is sourced from
the VMs on the hosts.
"""


from __future__ import annotations

import logging

from typing import Iterator, TYPE_CHECKING
from setproctitle import setproctitle
from cattrs import unstructure, structure
from premiscale.config.v1alpha1 import Host


if TYPE_CHECKING:
    from premiscale.config.v1alpha1 import Config
    from premiscale.metrics.state._base import State
    from premiscale.metrics.timeseries._base import TimeSeries


log = logging.getLogger(__name__)


def build_timeseries_connection(config: Config) -> TimeSeries:
    """
    Build a metrics collection class instance for storing metrics  hosts. Only one of
    these loops is created; metrics are published to influxdb for retrieval and query
    by the ASG loop, which evaluates on a per-ASG basis whether Actions need to be taken.

    Args:
        config (Config): The configuration object.

    Returns:
        TimeSeries: A time-series database interface.

    Raises:
        ValueError: If the time-series database type is unknown.
    """
    match config.controller.databases.timeseries.type:
        case 'memory':
            log.debug(f'Using local memory for time series database.')
            from premiscale.metrics.timeseries.local import Local

            return Local(config)
        case 'influxdb':
            log.debug(f'Using InfluxDB for time series database.')
            from premiscale.metrics.timeseries.influxdb import InfluxDB

            connection = unstructure(config.controller.databases.timeseries.connection)
            del(connection['type'])

            return InfluxDB(**connection)
        case _:
            raise ValueError(f'Unknown timeseries database type: {config.controller.databases.timeseries.type}')


def build_state_connection(config: Config) -> State:
    """
    Build a state collection class.

    Args:
        config (Config): The configuration object.

    Returns:
        State: A state database interface.

    Raises:
        ValueError: If the state database type is unknown.
    """
    match config.controller.databases.state.type:
        case 'memory':
            # SQLite
            log.debug(f'Using local memory for state database.')
            from premiscale.metrics.state.local import Local

            return Local()
        case 'mysql':
            log.debug(f'Using MySQL for state database.')
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

        # Set up database interfaces.
        if self.timeseries_enabled:
            log.debug(f'Opening time series database connection.')
            self.timeseriesConnection = build_timeseries_connection(self.config)

        log.debug('Opening state database connection.')
        self.stateConnection = build_state_connection(self.config)

    def hostIterator(self) -> Iterator:
        """
        Create an iterator that visits every host specified in the configuration file.
        """
        return iter(self.config.controller.autoscale.hosts)

    def hostCollect(self, host: Host) -> None:
        """
        Collect metrics from a host and store them in the appropriate backend database.
        """

    def vmCollect(self, host: Host) -> None:
        """
        Collect metrics from a VM and store them in the appropriate backend database.
        """
        pass
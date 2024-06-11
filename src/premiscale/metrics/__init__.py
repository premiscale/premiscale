"""
A module for handling metrics collection from hosts. This includes time-series and state data.
The distinguishing factor between state and time-series data is where it's sourced from; state
data is sourced from the hosts on which the VMs reside, while time-series data is sourced from
the VMs on the hosts.
"""


from __future__ import annotations

import logging

from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING
from setproctitle import setproctitle
from cattrs import unstructure
from time import sleep
from premiscale.hypervisor import build_hypervisor_connection


if TYPE_CHECKING:
    from typing import Iterator
    from premiscale.config.v1alpha1 import Config, Host
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

        # Set up database interfaces.
        if self.timeseries_enabled:
            log.debug(f'Opening time series database connection.')
            self.timeseriesConnection = build_timeseries_connection(self.config)
            self.timeseriesConnection.open()

        log.debug('Opening state database connection.')
        self.stateConnection = build_state_connection(self.config)
        self.stateConnection.open()

        self._collectMetrics()

    def __iter__(self) -> Iterator:
        """
        Create an iterator that visits every host specified in the configuration file.
        """
        return iter(self.config.controller.autoscale.hosts)

    def __len__(self) -> int:
        """
        Return the number of hosts specified in the configuration file.
        """
        return len(self.config.controller.autoscale.hosts)

    def _collectMetrics(self) -> None:
        """
        Collect metrics from all hosts and store them in the appropriate backend database.
        """
        while True:
            # Paginate through hosts to avoid OOM errors for large numbers of hosts.
            for page in range(0, len(self), self.config.controller.databases.maxHostConnectionThreads):
                log.debug(f'Collecting metrics for hosts {page} to {page + self.config.controller.databases.maxHostConnectionThreads}.')

                threads = []
                lower_bound = page * self.config.controller.databases.maxHostConnectionThreads
                upper_bound = (page + self.config.controller.databases.maxHostConnectionThreads) if (page + self.config.controller.databases.maxHostConnectionThreads) < len(self) else len(self)

                with ThreadPoolExecutor(max_workers=self.config.controller.databases.maxHostConnectionThreads) as executor:
                    for i, host in enumerate(self):
                        if i < lower_bound or i >= upper_bound:
                            # Skip adding these ones until we're in the correct range.
                            continue

                        threads.append(
                            executor.submit(
                                self._collectHostMetrics,
                                host
                            )
                        )

                    for thread in threads:
                        if thread is not None:
                            thread.result()

                sleep(self.config.controller.databases.collectionInterval)

    def _collectHostMetrics(self, host: Host) -> None:
        """
        Collect metrics for a single host over a Libvirt connection and store them in the appropriate backend database.
        """
        with build_hypervisor_connection(host) as host_connection:
            # state_data = self._collectStateMetrics(host_connection)

            # Diff current state and recorded state and update the state database.

            if self.timeseries_enabled:
                # timeseries_data = self._collectVirtualMachineMetrics(host)
                pass
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
from datetime import datetime, timedelta
from premiscale.hypervisor import build_hypervisor_connection


if TYPE_CHECKING:
    from typing import Iterator, List
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

    Args:
        config (Config): The configuration object.
        timeseries_enabled (bool): Whether to enable time-series data collection. Defaults to False.
    """
    def __init__(self, config: Config, timeseries_enabled: bool = False) -> None:
        self.timeseriesConnection: TimeSeries | None = None
        self.timeseries_enabled = timeseries_enabled
        self.config = config

    def __call__(self) -> None:
        """
        Start the metrics collection subprocess.
        """
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

        Returns:
            Iterator: An iterator that visits every host.
        """
        return iter(self.config.controller.autoscale.hosts)

    def __len__(self) -> int:
        """
        Return the number of hosts specified in the configuration file.

        Returns:
            int: The number of hosts.
        """
        return len(self.config.controller.autoscale.hosts)

    def __getitem__(self, subscript: int | slice) -> List[Host]:
        """
        Get a host by index or slice.

        Args:
            subscript (int | slice): The index or slice of the hosts to retrieve.

        Returns:
            List[Host]: List of hosts at the specified index or within the range of the slice.
        """
        if isinstance(subscript, slice):
            return self.config.controller.autoscale.hosts[subscript.start:subscript.stop:subscript.step]
        else:
            return [self.config.controller.autoscale.hosts[subscript]]

    def _collectMetrics(self) -> None:
        """
        Collect metrics from all hosts and store them in the appropriate backend database.
        """
        while True:
            collection_run_start = datetime.now()

            # Paginate through hosts to avoid queuing up a large number of jobs to visit hosts.
            for page in range(0, len(self) // self.config.controller.databases.maxHostConnectionThreads + 1):

                # Set a lower and upper bound for a slice of hosts to visit from the whole config.
                lower_bound = page * self.config.controller.databases.maxHostConnectionThreads
                _potential_upper_bound = (1 + page) * self.config.controller.databases.maxHostConnectionThreads
                upper_bound = _potential_upper_bound if _potential_upper_bound < len(self) else len(self)

                if lower_bound == upper_bound:
                    log.debug(f'No hosts to visit. Ensure you list managed hosts in the config file.')
                    break

                log.debug(f'Collecting metrics for hosts {lower_bound} to {upper_bound}.')

                # Reset our collection of threads every paginated iteration over hosts.
                threads = []

                with ThreadPoolExecutor(max_workers=self.config.controller.databases.maxHostConnectionThreads) as executor:
                    for host in self[lower_bound:upper_bound]:
                        threads.append(
                            executor.submit(
                                self._collectHostMetrics,
                                host
                            )
                        )

                    for thread in threads:
                        if thread is not None:
                            thread.result()

            # Wait for the next collection interval, or start right away if collection took longer than that interval.

            collection_run_end = datetime.now()
            collection_run_duration = round((collection_run_end - collection_run_start).total_seconds(), 2)

            log.debug(f'Collection run took {collection_run_duration} seconds.')

            if collection_run_duration < round(timedelta(seconds=self.config.controller.databases.collectionInterval).total_seconds(), 2):
                actual_sleep = round(self.config.controller.databases.collectionInterval - (collection_run_end - collection_run_start).total_seconds(), 2)
                log.debug(f'Waiting for {actual_sleep} seconds before revisiting every host.')
                sleep(actual_sleep)
            else:
                log.warning(f'Collection took longer than the collection interval of {self.config.controller.databases.collectionInterval} seconds. Starting collection immediately.')

    def _collectHostMetrics(self, host: Host) -> None:
        """
        Collect metrics for a single host over a Libvirt connection and store them in the appropriate backend database.
        """
        with build_hypervisor_connection(host) as host_connection:
            log.info(f'Collecting metrics for host {host.name}.')
            # state_data = self._collectStateMetrics(host_connection)

            # Diff current state and recorded state and update the state database.

            if self.timeseries_enabled:
                # timeseries_data = self._collectVirtualMachineMetrics(host)
                pass
"""
Reconcile metrics and state databases and place Actions on the autoscaling queue for the Autoscaling subprocess.
"""


from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from datetime import datetime, timezone, timedelta
from time import sleep
from setproctitle import setproctitle

from premiscale.metrics import (
    build_state_connection,
    build_timeseries_connection
)

from premiscae.autoscaling.actions import (
    Verb,
    Null,
    Create,
    Migrate,
    Clone,
    Replace,
    Delete
)

if TYPE_CHECKING:
    from premiscale.config.v1alpha1 import Config
    from multiprocessing.queues import Queue


log = logging.getLogger(__name__)


class Reconcile:
    """
    Internal reconciliation queries metrics and state databases and places Actions on the autoscaling
    queue for the Autoscaling subprocess to handle.

    Args:
        config (Config): The parsed, user-provided config file.
    """
    def __init__(self, config: Config) -> None:
        # Database connections
        self.state_database = build_state_connection(config)
        self.metrics_database = build_timeseries_connection(config)

        # Queues
        self.platform_queue: Queue
        self.asg_queue: Queue

        self._config = config

    def __call__(self, asg_queue: Queue, platform_queue: Queue) -> None:
        setproctitle('reconcile')

        self.asg_queue = asg_queue
        self.platform_queue = platform_queue

        log.debug('Starting reconciliation subprocess')

        self._reconcile()

    def _reconcile(self) -> None:
        """
        Reconcile metrics and state databases and place Actions on the autoscaling queue for the Autoscaling subprocess.
        """
        while True:
            reconciliation_run_start = datetime.now(timezone.utc)

            # Reconcile metrics and state databases into queued actions to bring the ASG back into the desired state.


            reconciliation_run_end = datetime.now(timezone.utc)

            reconciliation_duration = round((reconciliation_run_end - reconciliation_run_start).total_seconds(), 2)
            log.debug(f'Reconciliation run took {reconciliation_duration}s')

            if reconciliation_duration > self._config.controller.reconciliation.interval:
                log.debug(f'Reconciliation run took longer than the interval of {self._config.controller.reconciliation.interval}s, starting another run immediately')
                continue
            else:
                log.debug(f'Sleeping for {self._config.controller.reconciliation.interval - reconciliation_duration}s')
                sleep(self._config.controller.reconciliation.interval - reconciliation_duration)

    def _create(self) -> None:
        """
        Add a Create-event to an autoscaling queue.
        """

    def _delete(self) -> None:
        """
        Add a Delete-event to an autoscaling queue.
        """

    def _null(self) -> None:
        """
        Add a Null-event to an autoscaling queue.
        """

    def _migrate(self) -> None:
        """
        Add a Migrate-event to an autoscaling queue.
        """

    def _clone(self) -> None:
        """
        Add a Clone-event to an autoscaling queue.
        """

    def _replace(self) -> None:
        """
        Add a Replace-event to an autoscaling queue.
        """

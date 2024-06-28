"""
Reconcile metrics and state databases and place Actions on the autoscaling queue for the Autoscaling subprocess to handle.
"""


from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from setproctitle import setproctitle
from premiscale.metrics import build_state_connection, build_timeseries_connection


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

    def __call__(self, asg_queue: Queue, platform_queue: Queue) -> None:
        setproctitle('reconcile')

        self.asg_queue = asg_queue
        self.platform_queue = platform_queue

        log.debug('Starting reconciliation subprocess')


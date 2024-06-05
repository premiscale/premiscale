import logging
import time

from multiprocessing.queues import Queue
from setproctitle import setproctitle
from premiscale.config.v1alpha1 import Config
from premiscale.controller.metrics import build_metrics
from premiscale.controller._state import build_state


log = logging.getLogger(__name__)


class Reconcile:
    """
    Similar to metrics - a reconciliation loop that queries influxdb for the list of VMs
    metrics came from and compares these data to state stored in MySQL. If they don't match,
    actions to correct the state drift are added to the queue.
    """
    def __init__(self, config: Config) -> None:
        self.state_database = build_state(config)
        self.metrics_database = build_metrics(config)
        self.platform_queue: Queue
        self.asg_queue: Queue

    def __call__(self, asg_queue: Queue, platform_queue: Queue) -> None:
        setproctitle('reconcile')
        self.asg_queue = asg_queue
        self.platform_queue = platform_queue
        log.debug('Starting reconciliation subprocess')
        while True:
            self.platform_queue.put('Hello')
            time.sleep(5)
        # Open database connections
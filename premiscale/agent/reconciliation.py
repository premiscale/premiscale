import logging
import time

from multiprocessing.queues import Queue
from setproctitle import setproctitle


log = logging.getLogger(__name__)


class Reconcile:
    """
    Similar to metrics - a reconciliation loop that queries influxdb for the list of VMs
    metrics came from and compares these data to state stored in MySQL. If they don't match,
    actions to correct the state drift are added to the queue.
    """
    def __init__(self, state_connection: dict, metrics_connection: dict) -> None:
        setproctitle('reconcile')
        match state_connection['type']:
            case 'mysql':
                from premiscale.state.mysql import MySQL
                del(state_connection['type'])
                self.state_database = MySQL(**state_connection)

        match metrics_connection['type']:
            case 'influxdb':
                from premiscale.metrics.influxdb import InfluxDB
                del(metrics_connection['type'])
                self.metrics_database = InfluxDB(**metrics_connection)

        self.platform_queue: Queue
        self.asg_queue: Queue

    def __call__(self, asg_queue: Queue, platform_queue: Queue) -> None:
        self.asg_queue = asg_queue
        self.platform_queue = platform_queue
        log.debug('Starting reconciliation subprocess')
        while True:
            self.platform_queue.put('Hello')
            time.sleep(5)
        # Open database connections
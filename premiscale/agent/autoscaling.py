import logging

from multiprocessing.queues import Queue
from setproctitle import setproctitle


log = logging.getLogger(__name__)


class ASG:
    """
    Handle actions. E.g., if a new VM needs to be created or deleted on some host,
    handle that action, and all relevant side-effects (e.g. updating MySQL state).

    One of these classes gets instantiated for every autoscaling group defined in
    the config.
    """
    def __init__(self) -> None:
        self.queue: Queue

    def __call__(self, asg_queue: Queue) -> None:
        setproctitle('autoscaling')
        self.queue = asg_queue
        log.debug('Starting autoscaling subprocess')
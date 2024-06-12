"""
Process queues of Actions for all autoscaling groups. This is the main entry point for the autoscaling subprocess.
"""


from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from multiprocessing.queues import Queue
from setproctitle import setproctitle
from premiscale.autoscaling.actions import Action


if TYPE_CHECKING:
    from premiscale.config.v1alpha1 import Config


log = logging.getLogger(__name__)


class Autoscaler:
    """
    Handle actions. E.g., if a new VM needs to be created or deleted on some host,
    handle that action, and all relevant side-effects (e.g. updating MySQL state).

    One of these classes gets instantiated for every autoscaling group defined in
    the config.
    """
    def __init__(self, config: Config) -> None:
        self.config = config
        self.queue: Queue

    def __call__(self, asg_queue: Queue) -> None:
        setproctitle('autoscaling')
        self.queue = asg_queue
        log.debug('Starting autoscaling subprocess')
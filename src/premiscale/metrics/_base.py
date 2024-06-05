"""
ABCs for metrics storage methods.
"""


from __future__ import annotations

import logging

from typing import Any
from abc import ABC
from setproctitle import setproctitle


log = logging.getLogger(__name__)


class Metrics(ABC):
    """
    An abstract base class with a skeleton interface for metrics class-types.
    """

    def __enter__(self) -> Metrics:
        return self

    def __exit__(self, *args: Any) -> None:
        return

    def __call__(self) -> None:
        setproctitle('metrics')
        log.debug('Starting metrics collection subprocess')
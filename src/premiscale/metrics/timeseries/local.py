"""
Methods for interacting with an in-memory metrics store.
"""


from __future__ import annotations

from typing import TYPE_CHECKING
from premiscale.metrics.timeseries._base import TimeSeries

if TYPE_CHECKING:
    from premiscale.config.v1alpha1 import Config


class Local(TimeSeries):
    """
    Implement required interface methods for storing host metrics in memory.
    """
    def __init__(self, config: Config) -> None:
        self.config = config
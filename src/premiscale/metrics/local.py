"""
Methods for interacting with an in-memory metrics store.
"""


from premiscale.metrics._base import Metrics
from premiscale.config.v1alpha1 import Config


class Local(Metrics):
    """
    Implement required interface methods for storing host metrics in memory.
    """
    def __init__(self, config: Config) -> None:
        self.config = config
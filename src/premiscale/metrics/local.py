"""
Methods for interacting with an in-memory metrics store.
"""


from premiscale.metrics._base import Metrics


class Local(Metrics):
    """
    Implement required interface methods for storing host metrics in memory.
    """
    def __init__(self) -> None:
        ...
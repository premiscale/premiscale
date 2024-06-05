"""
ABCs for metrics storage methods.
"""

from typing import Any
from abc import ABC


class Metrics(ABC):
    """
    An abstract base class with a skeleton interface for metrics class-types.
    """

    def __enter__(self) -> 'Metrics':
        return self

    def __exit__(self, *args: Any) -> None:
        return

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError('Metrics.__call__')
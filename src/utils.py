"""
General, helpful utils for use throughout the modules.
"""

from functools import partial

import sys


__all__ = [
    'errprint'
]


# TODO: replace with logging module.
errprint = partial(print, sys.stderr)

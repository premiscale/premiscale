"""
General, helpful utils for use throughout the modules.
"""

from functools import partial

import sys


__all__ = [
    'errprint'
]


errprint = partial(print, sys.stderr)

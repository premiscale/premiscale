"""
This module contains utility functions for the API.
"""


import multiprocessing as mp


def automatic_workers_count() -> int:
    """
    Automatically determine the number of workers to use for the API.

    Returns:
        int: number of workers to use.
    """
    return (mp.cpu_count() * 2) + 1
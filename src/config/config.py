"""
Parse a configuration file, or create a default one.
"""

from typing import Union

from pathlib import Path

import os


def config_exists(path: Union[str, Path]) -> bool:
    """
    Determine if a configuration file exists.

    Args:
        path (Union[str, Path]): path to config file.

    Returns:
        bool: Whether the config exists.
    """
    return Path.exists(Path(path))


def make_default(path: Union[str, Path]) -> None:
    """
    Make a default config file if one does not exist.

    Args:
        path (Union[str, Path]): The default location to create an autoscale configuration file, if it doesn't exist.

    Raises:
        PermissionError: If the daemon doesn't have the required permissions to create the default conf.
    """
    if not config_exists(path):
        os.mkdir(Path(path).parent)
        with open(str(path), 'x') as f, open('conf/default.yaml', 'r') as conf:
            f.write(conf.read().strip())

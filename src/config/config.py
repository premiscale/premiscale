"""
Parse a configuration file, or create a default one.
"""

from typing import Union

from pathlib import Path
from .validate import validate
from utils import errprint

import os


def initialize(config_path: str) -> None:
    """
    Initialize the agent with directories and configuration files.
    """
    if not Path.exists(Path(config_path)):
        make_default(config_path)

    with open(config_path, 'r') as config:
        msg, ret = validate(config.read().rstrip())
        if not ret:
            errprint(f'Config file is not valid:\n\n{msg}')


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
    try:
        if not Path.exists(Path(path).parent):
            Path.mkdir(Path(path).parent)
        if not config_exists(path):
            with open(str(path), 'x') as f, open('conf/default.yaml', 'r') as conf:
                f.write(conf.read().strip())
    except PermissionError as msg:
        errprint('premiscale does not have permission to install to /opt, must run as root.')
        exit(1)
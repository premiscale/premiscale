"""
Controller utils.
"""


from __future__ import annotations

import sys
import logging
import json
import os

from enum import Enum
from pathlib import Path


log = logging.getLogger(__name__)


class LogLevel(Enum):
    info = logging.INFO
    error = logging.ERROR
    warn = logging.WARNING
    debug = logging.DEBUG

    def __str__(self):
        return self.name

    @classmethod
    def from_string(cls, s: str) -> LogLevel:
        """
        Convert a string to the enum value.

        Args:
            s (str): key to convert to the enum value.

        Returns:
            LogLevel: Log level object.
        """
        try:
            return cls[s.lower()]
        except KeyError:
            log.error('Must specify an accepted log level')
            sys.exit(1)


def validate_port(number: str | int, port_name: str | None = None) -> int:
    """
    Validates port number as a string or int.

    Args:
        number (str | int): the port number as either an int or a str.
        port_name (str | None): the name of the port (to use in error messages).

    Returns:
        int: the port number, if it passes all checks.
    """
    try:
        _number = int(number)
    except ValueError:
        if port_name:
            log.error(f'expected a valid port number "{port_name}", received: "{number}"')
        else:
            log.error(f'expected a valid port number, received: "{number}"')
        sys.exit(1)

    if 0x0 > _number > 0xFFFF:
        if port_name:
            log.error(f'port "{port_name}" must be in range 0 < port < 65535, received: "{number}"')
        else:
            log.error(f'port must be in range 0 < port < 65535, received: "{number}"')
        sys.exit(1)

    return _number


def write_json(data: dict, path: str) -> None:
    """
    Write a dictionary to a JSON file.

    Args:
        data (dict): the dictionary to write.
        path (str): the path to write the file to.
    """
    path_e = os.path.expandvars(path)

    try:
        with open(path_e, 'w', encoding='utf-8') as f:
            log.debug(f'Writing JSON to file: {path_e}')
            json.dump(data, f)
    except (FileNotFoundError, PermissionError) as msg:
        log.error(f'Failed to write JSON file, received: {msg}')
    except OSError as msg:
        log.error(f'Failed to write JSON file {path_e}, received: {msg}. Check your path and permissions')


def read_json(path: str) -> dict | None:
    """
    Read a JSON file and return the data as a dictionary.

    Args:
        path (str): the path to the JSON file.

    Returns:
        dict | None: the data from the JSON file, or None if the file does not exist.
    """
    try:
        if Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except (FileNotFoundError, PermissionError) as msg:
        log.error(f'Failed to read JSON file, received: {msg}')
        return None
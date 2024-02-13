"""
Controller utils.
"""


import sys
import logging

from enum import Enum

log = logging.getLogger(__name__)


class LogLevel(Enum):
    info = logging.INFO
    error = logging.ERROR
    warn = logging.WARNING
    debug = logging.DEBUG

    def __str__(self):
        return self.name

    @classmethod
    def from_string(cls, s: str) -> 'LogLevel':
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
            log.error('Must specify an accepted log level.')
            sys.exit(1)


def validate_port(number: str | int, port_name: str | None = None) -> int:
    """
    Validates port number as a string or int.

    Args:
        number (Union[int, str]): the port number as either an int or a str.

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
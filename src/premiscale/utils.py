"""
Controller utils.
"""


import sys
import logging
import json
import time

from typing import Callable, Any, Dict
from enum import Enum
from pathlib import Path
from functools import wraps
from urllib.error import URLError
from premiscale.exceptions import RateLimitedError


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


def write_json(data: dict, path: str) -> None:
    """
    Write a dictionary to a JSON file.

    Args:
        data (dict): the dictionary to write.
        path (str): the path to write the file to.
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            log.debug(f'Writing JSON to file: {path}')
            json.dump(data, f)
    except (FileNotFoundError, PermissionError) as msg:
        log.error(f'Failed to write JSON file, received: {msg}')


def read_json(path: str) -> dict | None:
    """
    Read a JSON file and return the data as a dictionary.

    Args:
        path (str): the path to the JSON file.

    Returns:
        dict: the data from the JSON file.
    """
    try:
        if Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except (FileNotFoundError, PermissionError) as msg:
        log.error(f'Failed to read JSON file, received: {msg}')
        return None


def retry(retries: int =0, retry_delay: float = 1.0, ratelimit_buffer: float = 0.25) -> Callable:
    """
    A request retry decorator that catches common request exceptions and retries the wrapped function call.

    Args:
        retries: number of times to retry the wrapped function call. When `0`, retries indefinitely. (default: 0)
        retry_delay: if retries is 0, this delay value (in seconds) is used between retries. (default: 1.0)
        ratelimit_buffer: a buffer (in seconds) to add to the delay when a rate limit is hit. (default: 0.25)

    Returns:
        Either the result of a successful function call (be it via retrying or not).

    Raises:
        ValueError: if `retries` is less than 0.
    """
    if retries < 0:
        raise ValueError(f'Expected positive `retries` values, received: "{retries}"')

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Dict | None:
            res: Any = None

            def call() -> Dict[str, str] | None:
                nonlocal res

                try:
                    return f(*args, **kwargs)
                except RateLimitedError as msg:
                    log.warning(f'Ratelimited, waiting "{msg.delay + ratelimit_buffer}"s before trying again')
                    time.sleep(msg.delay + ratelimit_buffer)
                    return None
                except URLError as msg:
                    log.warning(msg)
                    return None

            if retries > 0:
                # Finite number of user-specified retries.
                for _ in range(retries):
                    if (res := call()) is not None:
                        return res
                else:
                    log.error(f'Retry attempt limit exceeded.')
                    return None
            else:
                # Infinite retries.
                while (res := call()) is None:
                    time.sleep(retry_delay)

                return res

        return wrapper
    return decorator
"""
PremiScale autoscaler agent.

© PremiScale, Inc. 2023
"""


import sys
import logging
import os

from typing import Union, Optional
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from importlib import metadata as meta
from enum import Enum
from src.premiscale.config.parse import initialize, validate, configparse
from src.premiscale.agent.daemon import start


version = meta.version('premiscale')

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
        try:
            return cls[s.lower()]
        except KeyError:
            log.error('Must specify an accepted log level.')
            sys.exit(1)


def validate_port(number: Union[str, int], port_name: Optional[str] = None) -> int:
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


def main() -> None:
    """
    Set up the CLI for PremiScale autoscaler.
    """
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=__doc__
    )

    parser.add_argument(
        '--token', type=str, default='',
        help='Platform registration token.'
    )

    parser.add_argument(
        '-d', '--daemon', action='store_true',
        help='Start agent as a daemon.'
    )

    parser.add_argument(
        '-c', '--config', type=str, default='/opt/premiscale/config.yaml',
        help='Configuration file path to use.'
    )

    parser.add_argument(
        '--validate', action='store_true',
        help='Validate the provided configuration file and exit.'
    )

    parser.add_argument(
        '--version', action='store_true',
        help='Display agent version.'
    )

    parser.add_argument(
        '--log-stdout', action='store_true',
        help='Log to stdout (for use in containerized deployments).'
    )

    parser.add_argument(
        '--pid-file', type=str, default='/opt/premiscale/premiscale.pid',
        help='Pidfile name to use for agent daemon.'
    )

    parser.add_argument(
        '--log-level', default='info', choices=list(LogLevel), type=LogLevel.from_string,
        help='Set the logging level.'
    )

    log_group = parser.add_mutually_exclusive_group()

    log_group.add_argument(
        '--log-file', type=str, default='/opt/premiscale/echoes.log',
        help='Specify the file the service logs to if --log-stdout is not set.'
    )

    log_group.add_argument(
        '--log-stdout', action='store_true',
        help='Log to stdout (for use in containerized deployments).'
    )

    parser.add_argument(
        '--host', type=str, default='app.premiscale.com',
        help='URL of the PremiScale platform.'
    )

    args = parser.parse_args()

    # Configure logger
    if args.log_stdout:
        logging.basicConfig(
            stream=sys.stdout,
            format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            level=args.log_level.value
        )
    else:
        try:
            logging.basicConfig(
                filename=args.log_file,
                format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                level=args.log_level.value,
                filemode='a'
            )
        except FileNotFoundError as msg:
            log.error(f'Failed to configure logging, received: {msg}')
            sys.exit(1)

    if args.version:
        log.info(f'premiscale v{version}')
        sys.exit(0)

    if args.validate:
        sys.exit(0 if validate(args.config)[1] else 1)

    if args.daemon:
        initialize(args.config)
        config = configparse(args.config)
        log.info(f'Starting premiscale agent v{version}')

        if (token := args.token) != '':
            log.debug('Registering agent with provided token')
        elif (token := os.getenv('PREMISCALE_TOKEN')) != '':
            log.debug('Registering agent with provided environment variable')
        else:
            log.warning('Platform registration token not present, starting agent in standalone mode')
            token = ''

        # Start the premiscale agent.
        sys.exit(
            start(
                '/opt/premiscale',
                args.pid_file,
                config,
                token,
                args.host
            )
        )
    else:
        initialize(args.config)
        log.info('PremiScale successfully initialized. Use \'--daemon\' to start the agent controller.')
"""
PremiScale autoscaler agent.

© PremiScale, Inc. 2023
"""


import sys
import logging
import os

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from importlib import metadata as meta

from src.premiscale.config.parse import initialize, validate, configparse
from src.premiscale.agent.daemon import start


version = meta.version('premiscale')


log = logging.getLogger(__name__)


def debug() -> bool:
    """
    Determine if the agent should be in debug based on an environment variable.

    https://stackoverflow.com/a/65407083
    """
    return os.getenv('PREMISCALE_DEBUG', 'False').lower() in ('true', '1', 't')


def main() -> None:
    """
    Set up the CLI for PremiScale autoscaler.
    """
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=__doc__
    )

    parser.add_argument(
        '-d', '--daemon', action='store_true', default=False,
        help='Start agent as a daemon.'
    )

    parser.add_argument(
        '-c', '--config', type=str, default='/opt/premiscale/config.yaml',
        help='Configuration file path to use.'
    )

    parser.add_argument(
        '--host', type=str, default='app.premiscale.com',
        help='URL of the PremiScale platform.'
    )

    parser.add_argument(
        '--token', type=str, default='',
        help='Token for registering the agent with the platform on start.'
    )

    parser.add_argument(
        '--validate', action='store_true', default=False,
        help='Validate the provided configuration file and exit.'
    )

    parser.add_argument(
        '--version', action='store_true', default=False,
        help='Display agent version.'
    )

    parser.add_argument(
        '--log-stdout', action='store_true', default=False,
        help='Log to stdout (for use in containerized deployments).'
    )

    parser.add_argument(
        '--pid-file', type=str, default='/opt/premiscale/premiscale.pid',
        help='Pidfile name to use for agent daemon.'
    )

    parser.add_argument(
        '--debug', action='store_true', default=False,
        help='Enable agent debug logging.'
    )

    args = parser.parse_args()

    # Configure logger
    if args.log_stdout:
        logging.basicConfig(
            stream=sys.stdout,
            format='%(asctime)s | %(levelname)s | %(message)s',
            level=(logging.DEBUG if args.debug or debug() else logging.INFO)
        )
    else:
        logging.basicConfig(
            stream=sys.stdout,
            format='%(message)s',
            level=(logging.DEBUG if args.debug or debug() else logging.INFO)
        )
    if args.debug or debug():
        log.info('Agent started in debug mode.')
        logging.getLogger('asyncio').setLevel(logging.WARNING)

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
        start('/opt/premiscale', args.pid_file, config, token, args.host)
    else:
        initialize(args.config)
        log.info('PremiScale successfully initialized. Use \'--daemon\' to start the agent controller.')
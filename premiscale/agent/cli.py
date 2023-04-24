"""
PremiScale autoscaler agent.

© PremiScale, Inc. 2023
"""


import sys
import logging
import os

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from importlib import metadata as meta

from premiscale.config.parse import initialize, validate, configparse
from premiscale.agent.daemon import wrapper


__version__ = meta.version('premiscale')


log = logging.getLogger(__name__)


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
        help='Start PremiScale as a daemon.'
    )

    parser.add_argument(
        '-c', '--config', type=str, default='/opt/premiscale/config.yaml',
        help='Configuration file path to use.'
    )

    parser.add_argument(
        '--host', type=str, default='https://app.premiscale.com',
        help='URL of your PremiScale host.'
    )

    parser.add_argument(
        '--token', type=str, default='',
        help='Token for registering the agent with the PremiScale platform on first start.'
    )

    parser.add_argument(
        '--validate', action='store_true', default=False,
        help='Validate the provided configuration file.'
    )

    parser.add_argument(
        '--version', action='store_true', default=False,
        help='Show premiscale version.'
    )

    parser.add_argument(
        '--log-stdout', action='store_true', default=False,
        help='Log to stdout (for use in containerized deployments).'
    )

    parser.add_argument(
        '--pid-file', type=str, default='/opt/premiscale/premiscale.pid',
        help='Pidfile name to use for daemon.'
    )

    parser.add_argument(
        '--debug', action='store_true', default=False,
        help='Turn on logging debug mode.'
    )

    args = parser.parse_args()

    # Configure logger.
    if args.debug or os.getenv('PREMISCALE_DEBUG') is True:
        log.info('Agent starting in debug mode.')
    if args.log_stdout:
        logging.basicConfig(
            stream=sys.stdout,
            format='%(asctime)s | %(levelname)s | %(message)s',
            level=(logging.DEBUG if args.debug or os.getenv('PREMISCALE_DEBUG') is True else logging.INFO)
        )
    else:
        logging.basicConfig(
            stream=sys.stdout,
            format='%(message)s',
            level=(logging.DEBUG if args.debug or os.getenv('PREMISCALE_DEBUG') is True else logging.INFO)
        )

    if args.version:
        log.info(f'premiscale v{__version__}')
        sys.exit(0)

    if args.validate:
        sys.exit(0 if validate(args.config)[1] else 1)

    if args.daemon:
        initialize(args.config)
        config = configparse(args.config)
        log.info(f'Starting premiscale agent v{__version__}')

        if (token := args.token):
            log.debug('Registering agent with provided token')
        elif (token := os.getenv('PREMISCALE_TOKEN')) is not None:
            log.debug('Registering agent with provided token environment variable')
        else:
            log.warning('Platform registration token not present, starting agent in standalone mode')
            token = ''

        wrapper('/opt/premiscale', args.pid_file, config, token, args.host)
    else:
        initialize(args.config)
        log.info('PremiScale successfully initialized. Use \'--daemon\' to start the agent controller.')
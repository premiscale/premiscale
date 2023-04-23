"""
PremiScale autoscaling agent.

© PremiScale, Inc. 2023
"""


from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from importlib import metadata as meta
import sys
import logging
import os

from premiscale.config.parse import initialize, validate, parse
from premiscale.agent.daemon import wrapper


__version__ = meta.version('premiscale')


log = logging.getLogger(__name__)
log.info(__doc__)


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
    if args.log_stdout:
        logging.basicConfig(
            stream=sys.stdout,
            format='%(asctime)s | %(levelname)s | %(message)s',
            level=(logging.DEBUG if args.debug else logging.INFO)
        )
    else:
        logging.basicConfig(
        stream=sys.stdout,
        format='%(message)s',
        level=(logging.DEBUG if args.debug else logging.INFO)
    )

    if args.debug:
        log.info('Agent started in debug mode.')
    if not args.token and not os.getenv('PREMISCALE_TOKEN'):
        log.info('Platform registration token neither set as argument nor environment variable \'PREMISCALE_TOKEN\', starting agent in standalone mode.')

    if args.version:
        log.info(f'premiscale v{__version__}')
        sys.exit(0)
    if args.validate:
        sys.exit(0 if validate(args.config)[1] else 1)

    if args.daemon:
        initialize(args.config)
        config = parse(args.config, check=args.validate)
        log.info('Entering daemon')

        wrapper(working_dir='/opt/premiscale', pid_file=args.pid_file, agent_config=config)
    else:
        initialize(args.config)
        log.info('PremiScale successfully initialized. Use \'--daemon\' to enter the main control loop.')
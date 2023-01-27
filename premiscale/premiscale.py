"""
PremiScale autoscaler agent.

© PremiScale, Inc. 2023
"""


from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys
import logging

from config.utils import initialize, validate, parse
from daemon.daemon import PremiScaleDaemon
from version import __version__


log = logging.getLogger(__name__)


def cli() -> None:
    """
    Set up the CLI for autoscaler.
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
        '--validate', type=str, default=False,
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

    if args.version:
        log.info(f'premiscale v{__version__}')
        sys.exit(0)
    elif args.validate:
        sys.exit(0 if validate(args.config)[1] else 1)

    if args.daemon:
        initialize(args.config)
        # config = parse(args.config)
        with PremiScaleDaemon() as d:
            d.start()
    else:
        initialize(args.config)
        print(parse(args.config))
        log.info('PremiScale successfully initialized. Use \'--daemon\' to enter the main control loop.')
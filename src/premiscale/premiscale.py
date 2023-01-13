"""
PremiScale autoscaler agent.

© PremiScale, Inc. 2023
"""


from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys

from config.config import initialize, validate
from version import __version__


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
        help='Start the autoscaling daemon.'
    )

    parser.add_argument(
        '-c', '--config', type=str, default='/opt/premiscale/premiscale.conf',
        help='Configuration file to use.'
    )

    parser.add_argument(
        '--validate', type=str, default=False,
        help='Validate the provided configuration file.'
    )

    parser.add_argument(
        '--version', action='store_true', default=False,
        help='Show premiscale version.'
    )

    args = parser.parse_args()

    if args.version:
        print(f'premiscale v{__version__}')
        sys.exit(0)

    if args.validate:
        sys.exit(0 if validate(args.config)[1] else 1)

    initialize(args.config)


if __name__ == '__main__':
    cli()

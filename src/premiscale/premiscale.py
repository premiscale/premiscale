"""
PremiScale autoscaler agent.
"""


from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from config.config import initialize

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
        '--version', action='store_true', default=False,
        help='Show premiscale version.'
    )

    args = parser.parse_args()

    if args.version:
        print(f'premiscale v{__version__}')
        exit(0)

    initialize(args.config)


if __name__ == '__main__':
    cli()

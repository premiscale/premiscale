"""
Autoscaler interface.
"""


from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from config.validate import validate
from config.config import make_default
from utils import errprint

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
        '-c', '--config', type=str, default='/etc/autoscaler/autoscale.conf',
        help='Configuration file to use.'
    )

    parser.add_argument(
        '--version', action='store_true', default=False,
        help='Show autoscaler version.'
    )

    args = parser.parse_args()

    if args.version:
        print(f'autoscale v{__version__}')
        exit(0)

    make_default(args.config)
    with open(args.config, 'r') as conf:
        msg, ret = validate(conf)
        if not ret:
            errprint(f'Config file is not valid:\n\n{msg}')



if __name__ == '__main__':
    cli()

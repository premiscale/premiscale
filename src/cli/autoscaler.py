"""
Autoscaler interface.
"""


from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from config import validate, config
from utils import errprint


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
        help='Start the autoscaling daemon. By default, this tool is a minimal client.'
    )

    parser.add_argument(
        '-c', '--config', type=str, default='/etc/autoscaler/autoscale.conf',
        help='Configuration file to use.'
    )

    args = parser.parse_args()

    config.make_default(args.config)
    with open(args.config, 'r') as conf:
        msg, ret = validate(conf)
        if not ret:
            errprint(f'Config file is not valid:\n\n{msg}')


if __name__ == '__main__':
    cli()

"""
PremiScale autoscaler.

© PremiScale, Inc. 2024
"""


import sys
import logging
import os

from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from importlib import metadata as meta

from premiscale.config.parse import initialize, validate, configparse
from premiscale.controller.daemon import start
from premiscale.controller.utils import LogLevel


version = meta.version('premiscale')

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
        '--token', type=str, default='',
        help='Platform registration token. Also available as the environment variable \'PREMISCALE_TOKEN\'.'
    )

    parser.add_argument(
        '-d', '--daemon', action='store_true',
        help='Start controller as a daemon.'
    )

    parser.add_argument(
        '-c', '--config', type=str, default='/opt/premiscale/config.yaml',
        help='Configuration file path to use. Also available as the environment variable \'PREMISCALE_CONFIG_PATH\'.'
    )

    parser.add_argument(
        '--validate', action='store_true',
        help='Validate the provided configuration file and exit.'
    )

    parser.add_argument(
        '--platform', type=str, default='app.premiscale.com',
        help='URL of the PremiScale platform. Also available as the environment variable \'PREMISCALE_PLATFORM\'.'
    )

    parser.add_argument(
        '--version', action='store_true',
        help='Display controller version.'
    )

    parser.add_argument(
        '--pid-file', type=str, default='/opt/premiscale/premiscale.pid',
        help='Pidfile name to use for the controller daemon. Also available as the environment variable \'PREMISCALE_PID_FILE\'.'
    )

    parser.add_argument(
        '--log-level', default='info', choices=list(LogLevel), type=LogLevel.from_string,
        help='Set the logging level. Also available as the environment variable \'PREMISCALE_LOG_LEVEL\'.'
    )

    log_group = parser.add_mutually_exclusive_group()

    log_group.add_argument(
        '--log-file', type=str, default='/opt/premiscale/controller.log',
        help='Specify the file the service logs to if --log-stdout is not set. Also available as the environment variable \'PREMISCALE_LOG_FILE\'.'
    )

    log_group.add_argument(
        '--log-stdout', action='store_true',
        help='Log to stdout (for use in containerized deployments).'
    )

    parser.add_argument(
        '--cacert', type=str, default='',
        help='Path to the certificate file (for use with self-signed certificates). Also available as the environment variable \'PREMISCALE_CACERT\'.'
    )

    args = parser.parse_args()

    if args.version:
        print(f'premiscale v{version}')
        sys.exit(0)

    # Configure logger
    if args.log_stdout:
        logging.basicConfig(
            stream=sys.stdout,
            format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            level=args.log_level.value
        )
    else:
        try:
            # Instantiate log path (when logging locally).
            if not Path(args.log_file).exists():
                Path(args.log_file).parent.mkdir(parents=True, exist_ok=True)

            logging.basicConfig(
                filename=args.log_file,
                format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                level=args.log_level.value,
                filemode='a'
            )
        except (FileNotFoundError, PermissionError) as msg:
            log.error(f'Failed to configure logging, received: {msg}')
            sys.exit(1)

    if args.validate:
        sys.exit(0 if validate(args.config)[1] else 1)

    if args.daemon:
        initialize(args.config)
        config = configparse(args.config)
        log.info(f'Starting PremiScale controller v{version}')

        if (token := args.token) != '':
            log.debug('Registering controller with provided token')
        elif (token := os.getenv('PREMISCALE_TOKEN')) != '':
            log.debug('Registering controller with provided environment variable')
        else:
            token = ''

        # Start the premiscale controller.
        sys.exit(
            start(
                '/opt/premiscale',
                args.pid_file,
                config,
                version,
                token,
                args.platform,
                args.cacert
            )
        )
    else:
        initialize(args.config)
        log.info('PremiScale successfully initialized. Use \'--daemon\' to start the controller.')
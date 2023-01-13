"""
Parse a configuration file, or create a default one.
"""


from typing import Union, Tuple

import sys
import logging
from pathlib import Path


import yamale


log = logging.getLogger(__name__)


def initialize(config_path: str) -> None:
    """
    Initialize the agent with directories and configuration files.
    """
    if not Path.exists(Path(config_path)):
        _make_default(config_path)

    with open(config_path, 'r', encoding='utf-8') as config:
        msg, ret = validate(config.read().rstrip())
        if not ret:
            log.error(f'Config file is not valid:\n\n{msg}')


def validate(config: str, schema: str = '../../schema/schema.yaml', strict: bool = True) -> Tuple[str, bool]:
    """
    Validate users' config files against our schema.

    Args:
        config: config file data to validate against the schema.
        schema: schema to use with config validation.
        strict: whether or not to use strict mode on yamale.

    Returns:
        bool: Whether or not the config conforms to our expected schema.
    """
    schema = yamale.make_schema(schema)

    try:
        yamale.validate(config, strict=strict)
        return '', True
    except ValueError as msg:
        return str(msg), False


def _config_exists(path: Union[str, Path]) -> bool:
    """
    Determine if a configuration file exists.

    Args:
        path (Union[str, Path]): path to config file.

    Returns:
        bool: Whether the config exists.
    """
    return Path.exists(Path(path))


def _make_default(path: Union[str, Path]) -> None:
    """
    Make a default config file if one does not exist.

    Args:
        path (Union[str, Path]): The default location to create an autoscale configuration file, if it doesn't exist.

    Raises:
        PermissionError: If the daemon doesn't have the required permissions to create the default conf.
    """
    try:
        if not Path.exists(Path(path).parent):
            Path.mkdir(Path(path).parent)
        if not _config_exists(path):
            with open(str(path), 'x', encoding='utf-8') as f, open('conf/default.yaml', 'r', encoding='utf-8') as conf:
                f.write(conf.read().strip())
    except PermissionError:
        log.error('premiscale does not have permission to install to /opt, must run as root.')
        sys.exit(1)
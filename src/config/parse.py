"""
Parse a configuration file, or create a default one.
"""


import sys
import logging
import json

from typing import Union, Tuple
from pathlib import Path

import yamale


log = logging.getLogger(__name__)


def initialize(config: Union[Path, str]) -> None:
    """
    Initialize the agent with directories and configuration files.

    Args:
        config_path: path to config file to either create or validate.
    """
    if not Path.exists(Path(config)):
        _make_default(config)

    with open(config, 'r', encoding='utf-8') as f:
        msg, ret = validate(f.read().rstrip())
        if not ret:
            log.error(f'Config file is not valid:\n\n{msg}')



def validate(config: str, schema: str = '../../conf/schema.yaml', strict: bool = True) -> Tuple[str, bool]:
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
        yamale.validate(schema, config, strict=strict)
        return '', True
    except ValueError as msg:
        return str(msg), False


def parse(config: str, check: bool = False) -> dict:
    """
    Parse a config file and return it as a dictionary (JSON).

    Args:
        config (str): path to the config file.
        check (bool): whether or not to validate the provided config file.

    Returns:
        dict: The parsed config file.
    """
    if check:
        validate(config)

    with open(config, 'r', encoding='utf-8') as f:
        return json.loads(f.read().rstrip())


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
            Path.mkdir(Path(path).parent, parents=True)
        if not _config_exists(path):
            with open(str(path), 'x', encoding='utf-8') as f, open('conf/default.yaml', 'r', encoding='utf-8') as conf:
                f.write(conf.read().strip())
    except PermissionError:
        log.error(f'premiscale does not have permission to install to {str(Path(path).parent)}, must run as root.')
        sys.exit(1)

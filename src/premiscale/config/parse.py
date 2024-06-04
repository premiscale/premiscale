"""
Parse a configuration file, or create a default one.
"""


import yamale
import yaml
import logging
import sys

from typing import Union, Tuple
from pathlib import Path
from importlib import resources
from cattrs import unstructure
from premiscale.config.v1alpha1 import Config


log = logging.getLogger(__name__)


__all__ = [
    'configParse',
    'validate'
]


def configParse(config: str) -> Config:
    """
    Parse a config file and return it as a Config-object. Optionally validate types and structure against the Yamale schema.

    Args:
        config (str): path to the config file.
        check (bool): whether or not to validate the provided config file.

    Returns:
        dict: The parsed config file.
    """
    # Drop a default config for parsing.
    if not Path(config).exists():
        makeDefaultConfig(config)

    with open(config, 'r', encoding='utf-8') as f:
        try:
            _config = Config.from_dict(
                yaml.safe_load(
                    f.read().rstrip()
                )
            )
        except (yaml.YAMLError, ValueError, KeyError) as e:
            log.error(f'Error parsing config file: {e}')
            sys.exit(1)

    log.debug(f'Successfully parsed config version {_config.version}: {unstructure(_config)}')
    return _config


def validate(data: dict, schema: str = 'schema.yaml', strict: bool = True) -> Tuple[str, bool]:
    """
    Validate users' config files against our schema.

    Args:
        config: config file path/name to validate against the schema.
        schema: schema file to use with config validation.
        strict: whether or not to use strict mode on yamale.

    Returns:
        bool: Whether or not the config conforms to our expected schema.
    """
    try:
        with resources.open_text('premiscale.config.schemas', schema) as schema_f:
            schema = yamale.make_schema(schema_f.name)
    except FileNotFoundError:
        log.error(f'Could not find schema "{schema}" for config: are you using a supported config version?')
        sys.exit(1)

    try:
        yamale.validate(schema, data, strict=strict)
        return '', True
    except ValueError as msg:
        return str(msg), False


def makeDefaultConfig(path: Union[str, Path], default_config: Union[str, Path] = 'default.yaml') -> None:
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

        if not Path(path).exists():
            log.debug(f'Config file at {path} does not exist. Creating default config file.')

            with resources.open_text('premiscale.config', str(default_config)) as default_f, open(str(path), 'x', encoding='utf-8') as f:
                f.write(default_f.read().strip())

            log.debug(f'Successfully created default config file at \'{str(path)}\'')
    except PermissionError:
        log.error(f'premiscale does not have permission to install to {str(Path(path).parent)}, must run as root.')
        sys.exit(1)

"""
Parse a configuration file, or create a default one.
"""

from typing import Optional, Any, Union, Tuple
from pathlib import Path

import yamale
import yaml
import logging
import sys
import importlib.resources as resources

from premiscale.config._config import Config


log = logging.getLogger(__name__)


def configparse(config: str, check: bool = False) -> Config:
    """
    Parse a config file and return it as a dictionary (JSON).

    Args:
        config (str): path to the config file.
        check (bool): whether or not to validate the provided config file.

    Returns:
        dict: The parsed config file.
    """
    with open(config, 'r', encoding='utf-8') as f:
        config_json = yaml.safe_load(f.read().rstrip())

    match config_json['version']:
        case 'v1alpha1':
            if check:
                msg, valid = validate(config, f'schema.{config_json["version"]}.yaml')
                if not valid:
                    log.error(msg)
                    sys.exit(1)
                else:
                    log.info(f'Config \'{config}\' is valid against schema version {config_json["version"]}')

            from premiscale.config.v1alpha1 import Config_v1alpha1

            conf = Config_v1alpha1(config_json)
            log.debug(f'Successfully parsed config {conf.version}: {conf}')
            return conf
        case _:
            log.error(f'Cannot parse config version, supplied \'{config_json["version"]}\'')
            sys.exit(1)


def initialize(config: Union[Path, str]) -> str:
    """
    If the config file does not exist, create a default one. This is just a side-effect function that handles
    the case where a config file is not mounted in the container.

    Args:
        config_path: path to config file to either create or validate.

    Returns:
        the contents of the config file for further processing.
    """
    if not Path.exists(Path(config)):
        _make_default(config)

    with open(config, 'r', encoding='utf-8') as f:
        return f.read().rstrip()


def validate(config: Union[Path, str], schema: str = 'schema.yaml', strict: bool = True) -> Tuple[str, bool]:
    """
    Validate users' config files against our schema.

    Args:
        config: config file path/name to validate against the schema.
        schema: schema file to use with config validation.
        strict: whether or not to use strict mode on yamale.

    Returns:
        bool: Whether or not the config conforms to our expected schema.
    """
    with resources.open_text('premiscale.config.data', schema) as schema_f:
        schema = yamale.make_schema(schema_f.name)

    data = yamale.make_data(config)

    try:
        yamale.validate(schema, data, strict=strict)
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
    if Path.exists(Path(path)):
        log.debug(f'Config file at {str(path)} exists.')
        return True
    else:
        log.debug(f'Config file at {str(path)} does not exist.')
        return False


def _make_default(path: Union[str, Path], default_config: Union[str, Path] = 'default.yaml') -> None:
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
            log.debug(f'Creating default config file at \'{str(path)}\'')
            with resources.open_text('premiscale.config.data', default_config) as default_f, open(str(path), 'x', encoding='utf-8') as f:
                f.write(default_f.read().strip())
            log.debug(f'Successfully created default config file at \'{str(path)}\'')
    except PermissionError:
        log.error(f'premiscale does not have permission to install to {str(Path(path).parent)}, must run as root.')
        sys.exit(1)

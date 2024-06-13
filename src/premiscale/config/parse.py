"""
Parse a configuration file, or create a default one.
"""


import yaml
import logging
import sys
import json

from pathlib import Path
from importlib import resources
from yamale import make_schema, make_data, validate as yamale_validate
from premiscale.config.v1alpha1 import Config
from premiscale.config import build_config_from_version


log = logging.getLogger(__name__)


__all__ = [
    'configParse',
    'validateConfig'
]


def configParse(configPath: str) -> Config:
    """
    Parse a config file and return it as a Config-object. If the file does not exist, create a default one.

    Args:
        configPath (str): path to the config file.

    Returns:
        Config: The parsed config file.
    """

    # Drop a default config for parsing if one was not provided by the user.
    if not Path(configPath).exists():
        makeDefaultConfig(configPath)

    with open(configPath, 'r', encoding='utf-8') as f:
        try:
            _loaded_config = yaml.safe_load(
                f.read().rstrip()
            )

            # Validate the config file against the schema.
            if 'version' not in _loaded_config:
                log.error('Config file is missing a version field')
                sys.exit(1)

            if not validateConfig(configPath, version=_loaded_config['version']):
                sys.exit(1)

            # Parse the config into a Config object, now.
            _config = build_config_from_version(_loaded_config['version']).from_dict(_loaded_config)
        except (yaml.YAMLError, KeyError) as e:
            log.error(f'Error parsing config file: {e}')
            sys.exit(1)

    log.debug(f'Successfully parsed config version {_config.version}: {json.dumps(_loaded_config)}')

    return _config


def validateConfig(configPath: str, version: str = 'v1alpha1', strict: bool = True) -> bool:
    """
    Validate users' config files against our schema.

    Args:
        configPath (str): path to a config file path/name to validate against the schema.
        version (str): the version of the config file to validate. (default: 'v1alpha1')
        strict (bool): whether or not to use strict mode on yamale. (default: True)

    Returns:
        bool: True if the config file is valid.
    """

    if not Path(configPath).exists():
        makeDefaultConfig(configPath)
    else:
        log.debug(f'Found config file at {configPath}')

    try:
        with resources.open_text('premiscale.config.schemas', f'schema.{version}.yaml') as schema_f:
            schema = make_schema(path=schema_f.name)
            data = make_data(path=configPath)

        yamale_validate(
            schema,
            data,
            strict=strict
        )

        log.info(f'Config file at {configPath} is valid')
    except FileNotFoundError as e:
        log.error(f'Could not find file: {e}')
        return False
    except ValueError as e:
        log.error(f'Error validating config file: {e}')
        return False

    return True


def makeDefaultConfig(path: str | Path, default_config: str | Path = 'default.yaml') -> None:
    """
    Make a default config file if one does not exist.

    Args:
        path (str | Path): The default location to create an autoscale configuration file, if it doesn't exist.
        default_config (str | Path): The default config file to use when creating a new config file. (default: 'default.yaml')
    """
    try:
        if not Path(path).parent.exists():
            Path(path).parent.mkdir(parents=True)

        if not Path(path).exists():
            log.debug(f'Config file at {path} does not exist. Creating default config file')

            with resources.open_text('premiscale.config', str(default_config)) as default_config_f, open(str(path), 'x', encoding='utf-8') as f:
                f.write(default_config_f.read().strip())

            log.debug(f'Successfully created default config file at \'{str(path)}\'')
    except PermissionError:
        log.error(f'premiscale does not have permission to install to {str(Path(path).parent)}')
        sys.exit(1)

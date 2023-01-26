"""
Utility methods for daemon.
"""

from typing import Union, Tuple
from pathlib import Path

import yamale
import yaml
import logging
import sys

from .parse import Config_v1_alpha_1


log = logging.getLogger(__name__)


# def read_credentials_env_prefix(env_prefix: str) -> Dict[str, str]:
#     """_summary_

#     Args:
#         env_prefix (Optional[str], optional): _description_. Defaults to None.

#     Returns:
#         Dict[str, str]: _description_
#     """
#     return {}


# def read_credential_env(variable: str) -> Dict[str, str]:
#     """_summary_

#     Args:
#         variable (str): _description_

#     Returns:
#         Dict[str, str]: _description_
#     """
#     return {}


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
        config_json = yaml.safe_load(f.read().rstrip())

    match config_json['version']:
        case 'v1-alpha1':
            conf = Config_v1_alpha_1(config_json)
            log.debug(f'Successfully parsed config {conf.version}: {conf}')
            return conf
        case _:
            log.error(f'Cannot parse config version, supplied \'{config_json["version"]}\'')
            sys.exit(1)


def initialize(config: Union[Path, str]) -> str:
    """
    Initialize the agent with directories and configuration files.

    Args:
        config_path: path to config file to either create or validate.

    Returns:
        the contents of the config file for further processing.
    """
    if not Path.exists(Path(config)):
        _make_default(config)

    msg, valid = validate(config)

    if not valid:
        log.error(f'Config file at \'{str(config)}\' is not valid: {msg}')
        sys.exit(1)
    else:
        log.debug(f'Config file at \'{str(config)}\' is valid.')
        with open(config, 'r', encoding='utf-8') as f:
            return f.read().rstrip()



def validate(config: Union[Path, str], schema: Union[Path, str] = 'conf/schema.yaml', strict: bool = True) -> Tuple[str, bool]:
    """
    Validate users' config files against our schema.

    Args:
        config: config file path/name to validate against the schema.
        schema: schema file to use with config validation.
        strict: whether or not to use strict mode on yamale.

    Returns:
        bool: Whether or not the config conforms to our expected schema.
    """
    schema = yamale.make_schema(schema)
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
            log.debug(f'Creating default config file at \'{str(path)}\'')
            with open(str(path), 'x', encoding='utf-8') as f, open('conf/default.yaml', 'r', encoding='utf-8') as conf:
                f.write(conf.read().strip())
            log.debug(f'Successfully created default config file at \'{str(path)}\'')
    except PermissionError:
        log.error(f'premiscale does not have permission to install to {str(Path(path).parent)}, must run as root.')
        sys.exit(1)

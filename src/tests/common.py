"""
Helper interface with common methods for managing the operator installation and making API calls.
"""

from typing import List
from importlib import resources
from subprocess import Popen, PIPE
from dataclasses import dataclass
from humps import camelize

import random
import string
import yaml
import logging


log = logging.getLogger(__name__)


@dataclass
class CommandOutput:
    """
    Dataclass to store the output, error, and return code of a command.
    """
    stdout: str
    stderr: str
    returnCode: int


def run(command: List[str], shell: bool = False, timeout: float = 300) -> CommandOutput:
    """
    Run a command and return the output, error, and return code.

    Args:
        command (List[str]): shell command to run as a string.
        shell (bool): whether to run the command in a shell. Defaults to False. (Note: shell=True is a security hazard.) Defaults to False.
        timeout (float): timeout in seconds. Defaults to 300.

    Returns:
        CommandOutput: output, error, and return code.
    """
    # print(' '.join(c if c != '' else '""' for c in command))

    with Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True, shell=shell, encoding='utf-8') as p:
        stdout, stderr = p.communicate(timeout=timeout) # blocking
        ret = CommandOutput(stdout.rstrip(), stderr.rstrip(), p.returncode)

    if ret.returnCode != 0:
        log.error(f'Command failed with return code {ret.returnCode}. {ret.stderr}')

    return ret


def load_data(file: str, dtype: str = 'crd', camelcase: bool = True) -> dict:
    """
    Load a YAML file into a dictionary.

    Args:
        file (str): The path to the YAML file.
        dtype (str): The type of data to load. Defaults to 'crd'.
        camelcase (bool): Whether to camelcase the keys of the dictionary. Defaults to True.

    Returns:
        dict: The dictionary representation of the YAML file.
    """
    with resources.open_text(f'test.data.{dtype}', f'{file}.yaml') as f:
        manifest = yaml.load(f, Loader=yaml.Loader)

        if camelcase:
            camelized_manifest = camelize(manifest)
        else:
            camelized_manifest = manifest

        # We undo the camelization of the 'metadata' field to ensure that users' cases and capitalization are respected.
        camelized_manifest['spec']['encryptedData'] = manifest['spec']['encryptedData']

        return camelized_manifest


def random_secret(length: int = 40) -> str:
    """
    Generate a random string of a specified length for use as a test secret.

    Args:
        length (int, optional): length of the random string. Defaults to 40.

    Returns:
        str: the random string.
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
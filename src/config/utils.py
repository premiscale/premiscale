"""
Utility methods for daemon.
"""

from typing import Dict
from json import loads


def read_credentials_f(filename: str) -> Dict[str, str]:
    """
    Get the creds for an account from a JSON-formatted file or from env.

    Args:
        filename: provide the file (with path) from which to read credentials.
        env_prefix: Prefix to search all env vars for and read into a {<key>: <value>}-store.
        variable: Specific variable to read and return.

    Returns:
        The file's contents as a dictionary.
    """
    with open(filename, 'r') as fh:
        return loads(fh.read())


def read_credentials_env_prefix(env_prefix: str) -> Dict[str, str]:
    """_summary_

    Args:
        env_prefix (Optional[str], optional): _description_. Defaults to None.

    Returns:
        Dict[str, str]: _description_
    """
    return {}


def read_credential_env(variable: str) -> Dict[str, str]:
    """_summary_

    Args:
        variable (str): _description_

    Returns:
        Dict[str, str]: _description_
    """
    return {}
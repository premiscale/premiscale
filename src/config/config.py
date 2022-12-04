"""
Parse a configuration file, or create a default one.
"""

from typing import Union

from pathlib import Path

import os


def make_default(default_location: Union[str, Path]) -> None:
    """
    Make a default config file if one does not exist.

    Args:
        default_location: The default location to create an autoscale configuration file, if it doesn't exist.

    Raises:
        PermissionError: If the daemon doesn't have the required permissions to create the default conf.
    """
    if not Path.exists(Path(default_location)):
        os.mkdir(Path(default_location).parent)
        with open(str(default_location), 'x') as f, open('conf/default.yaml', 'r') as conf:
            f.write(conf.read().strip())

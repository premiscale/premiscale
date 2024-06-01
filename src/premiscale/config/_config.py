"""
Implement common methods all Config-<version> classes should inherit.
"""


from abc import ABC

import json


class Config(ABC, dict):
    """
    Parse a config dictionary into an object with methods to interact with the config.
    """
    def __init__(self, config: dict):
        self.config = config

    def version(self) -> str:
        """
        Get the version of the config.
        """
        return self.config['version']

    def json(self) -> str:
        """
        Return the config as a JSON object for debugging.
        """
        return json.dumps(self.config)
"""
Implement common methods all Config-<version> classes should inherit.
"""


class Config(dict):
    """
    Parse a config dictionary into an object with methods to interact with the config.
    """
    def __init__(self, config: dict):
        self.config = config

    def version(self) -> str:
        """
        Get the version of the config.
        """
        return self.config.config.version  # type: ignore
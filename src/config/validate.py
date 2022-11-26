"""
Validate a config file.
"""

import yamale


schema = yamale.make_schema('schema/schema.yaml')


def validate() -> bool:
    """
    Validate users' config files against our schema.

    Returns:
        bool: Whether or not the config conforms to our expected schema.
    """
    return False

"""
Validate a config file.
"""


from typing import Tuple

import yamale


schema = yamale.make_schema('schema/schema.yaml')


def validate(config: str, strict: bool = True) -> Tuple[str, bool]:
    """
    Validate users' config files against our schema.

    Args:
        config: config file data to validate against the schema.
        strict: whether or not to use strict mode on yamale.

    Returns:
        bool: Whether or not the config conforms to our expected schema.
    """
    try:
        yamale.validate(config, strict=strict)
        return '', True
    except ValueError as msg:
        return str(msg), False

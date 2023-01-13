"""
Validate a PremiScale config file.
"""


from typing import Tuple

import yamale


def validate(config: str, schema: str = '../../schema/schema.yaml', strict: bool = True) -> Tuple[str, bool]:
    """
    Validate users' config files against our schema.

    Args:
        config: config file data to validate against the schema.
        schema: schema to use with config validation.
        strict: whether or not to use strict mode on yamale.

    Returns:
        bool: Whether or not the config conforms to our expected schema.
    """
    schema = yamale.make_schema(schema)

    try:
        yamale.validate(config, strict=strict)
        return '', True
    except ValueError as msg:
        return str(msg), False

"""
Make the environment variables' values that we care about, portable.
"""


from typing import Dict
from ipaddress import IPv4Address, AddressValueError
from pathlib import Path

import os
import logging
import sys


log = logging.getLogger(__name__)


# TODO: implement import
# __all__ = [

# ]


env: Dict[str, str] = {
    # Environment variables to configure the operator (kopf).

}


# Environment type validation.
try:
    # float(env[''])
    ...
except (ValueError, AddressValueError) as e:
    log.error(e)
    sys.exit(1)
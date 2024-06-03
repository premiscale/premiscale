"""
Make the environment variables' values that we care about, portable.
"""


from typing import Dict
from ipaddress import AddressValueError

import os
import logging
import sys


log = logging.getLogger(__name__)


# TODO: implement import
# __all__ = [

# ]


env: Dict[str, str] = {
    # Environment variables to configure the operator (kopf).
    'PREMISCALE_TOKEN': os.getenv('PREMISCALE_TOKEN', ''),
    'PREMISCALE_CONFIG_PATH': os.getenv('PREMISCALE_CONFIG_PATH', '/opt/premiscale/config.yaml'),
    'PREMISCALE_PID_FILE': os.getenv('PREMISCALE_PID_FILE', '/opt/premiscale/premiscale.pid'),
    'PREMISCALE_LOG_LEVEL': os.getenv('PREMISCALE_LOG_LEVEL', 'info'),
    'PREMISCALE_LOG_FILE': os.getenv('PREMISCALE_LOG_FILE', '/opt/premiscale/controller.log'),
    'PREMISCALE_PLATFORM': os.getenv('PREMISCALE_PLATFORM', 'app.premiscale.com'),
    'PREMISCALE_CACERT': os.getenv('PREMISCALE_CACERT', ''),
}


# Environment type validation (if any).
try:
    ...
except (ValueError, AddressValueError) as e:
    log.error(e)
    sys.exit(1)
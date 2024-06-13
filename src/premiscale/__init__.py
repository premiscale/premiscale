"""
Make the environment variables' values that we care about, portable.
"""


from __future__ import annotations

from typing import TYPE_CHECKING
from importlib import metadata as meta

import os
import logging


if TYPE_CHECKING:
    from typing import Dict


log = logging.getLogger(__name__)


env: Dict[str, str] = {
    # Environment variables with default values to configure PremiScale.
    'PREMISCALE_TOKEN': os.getenv('PREMISCALE_TOKEN', ''),
    'PREMISCALE_CONFIG_PATH': os.getenv('PREMISCALE_CONFIG_PATH', '/opt/premiscale/config.yaml'),
    'PREMISCALE_CACERT': os.getenv('PREMISCALE_CACERT', ''),
    'PREMISCALE_LOG_LEVEL': os.getenv('PREMISCALE_LOG_LEVEL', 'info'),
    'PREMISCALE_LOG_FILE': os.getenv('PREMISCALE_LOG_FILE', '/opt/premiscale/controller.log'),
}

version: str = meta.version('premiscale')
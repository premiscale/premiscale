"""
Parse config files with the v1alpha1 config-parsing class.
"""


from typing import Optional, Any
from premiscale.config._config import Config

import logging


log = logging.getLogger(__name__)


class Config_v1_alpha_1(Config):
    """
    Class that encapsulates access methods and parsing config version v1alpha1.
    """
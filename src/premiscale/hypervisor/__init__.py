"""
Provide high-level methods for interfacing with hypervisors and hosts.
"""


from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from premiscale.hypervisor.qemu import Qemu
from premiscale.hypervisor.xen import Xen
from premiscale.hypervisor.esx import ESX


if TYPE_CHECKING:
    from premiscale.hypervisor._base import Libvirt
    from premiscale.config.v1alpha1 import Config


log = logging.getLogger(__name__)
"""
Provide high-level methods for interfacing with hypervisors and hosts.
"""


from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from cattr import unstructure


if TYPE_CHECKING:
    from premiscale.hypervisor._base import Libvirt
    from premiscale.config.v1alpha1 import Host


log = logging.getLogger(__name__)


def build_hypervisor_connection(host: Host) -> Libvirt:
    """
    Build a Libvirt connection object based on the user-provided configuration of the host.
    """
    conf = unstructure(host)

    match host.hypervisor:
        case 'qemu':
            log.debug(f'Using QEMU hypervisor for host {host.name} at {host.address}.')
            from premiscale.hypervisor.qemu import Qemu

            return Qemu(**conf)
        case 'vmware':
            log.debug(f'Using VMware hypervisor for host {host.name} at {host.address}.')
            from premiscale.hypervisor.vmware import VMware

            return VMware(**conf)
        case 'xen':
            log.debug(f'Using Xen hypervisor for host {host.name} at {host.address}.')
            from premiscale.hypervisor.xen import Xen

            return Xen(**conf)
        case _:
            raise ValueError(f'Unknown hypervisor type: {host.hypervisor}')
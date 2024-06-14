"""
Implement a Libvirt connection to a Qemu-based hypervisor/host.
"""


from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from premiscale.hypervisor._base import Libvirt


if TYPE_CHECKING:
    from typing import Dict
    from ipaddress import IPv4Address

log = logging.getLogger(__name__)


class Qemu(Libvirt):
    """
    A subclass for interacting with a Qemu-based hypervisor/host.
    """

    def __init__(self,
                 name: str,
                 address: IPv4Address,
                 port: int,
                 protocol: str,
                 timeout: int = 60,
                 user: str | None = None,
                 readonly: bool = False,
                 resources: Dict | None = None) -> None:
        super().__init__(
            name=name,
            address=address,
            port=port,
            protocol=protocol,
            hypervisor='qemu',
            timeout=timeout,
            user=user,
            readonly=readonly,
            resources=resources
        )

    def getHostState(self) -> Dict:
        """
        Get the state of the VMs on the host.

        Returns:
            Dict: The state of the VMs on the host.
        """
        if self._connection is None:
            return {}

        return {
            'virtualMachines': {
                vm.name(): vm.state() for vm in self._connection.listAllDomains()
            }
        }

    def getHostStats(self) -> Dict:
        """
        Get a report of schedulable resource utilization on the host.

        Returns:
            Dict: The resources available on the host.
        """
        if self._connection is None:
            return {}

        return {
            'hostStats': {
                'cpu': self._connection.getCPUStats(True),
                'memory': self._connection.getMemoryStats(-1, 0)
            }
        }

    def getHostVMStats(self) -> Dict:
        """
        Get a report of resource utilization for a VM.

        Returns:
            Dict: The resources utilized by the VM.
        """
        if self._connection is None:
            return {}

        stats: Dict[str, Dict] = {'vmStats': {}}

        for vm in self._connection.listAllDomains():
            vm_conf = self._connection.lookupByName(vm)

            log.debug(f"VM: {vm_conf}")

            stats['vmStats'][vm] = {
                'cpu': vm_conf.getCPUStats(True),
                'memory': vm_conf.memoryStats()
            }

        return stats
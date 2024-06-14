"""
Implement a Libvirt connection to an ESX-based hypervisor/host.
"""


from __future__ import annotations

from typing import TYPE_CHECKING
from premiscale.hypervisor._base import Libvirt


if TYPE_CHECKING:
    from typing import Dict
    from ipaddress import IPv4Address


class ESX(Libvirt):
    """
    Connect to an ESX hypervisor.
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
            hypervisor='esx',
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
        return {}

    def getHostStats(self) -> Dict:
        """
        Get a report of schedulable resource utilization on the host.

        Returns:
            Dict: The resources available on the host.
        """
        return {}

    def getHostVMStats(self) -> Dict:
        """
        Get a report of resource utilization for a VM.

        Returns:
            Dict: The resources utilized by the VM.
        """
        return {}
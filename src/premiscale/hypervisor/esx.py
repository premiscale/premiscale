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

    def __init__(self, name: str, address: IPv4Address, port: int, protocol: str, timeout: int = 30, user: str | None = None, readonly: bool = False, resources: Dict | None = None) -> None:
        super().__init__(
            name=name,
            address=address,
            port=port,
            user=user,
            protocol=protocol,
            readonly=readonly,
            hypervisor='esx',
            resources=resources
       )
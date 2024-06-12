"""
Implement a Libvirt connection to a Qemu-based hypervisor/host.
"""


from __future__ import annotations

from typing import TYPE_CHECKING
from premiscale.hypervisor._base import Libvirt


if TYPE_CHECKING:
    from ipaddress import IPv4Address


class Qemu(Libvirt):
    """
    Connect to a host with a Qemu hypervisor.
    """

    def __init__(self, name: str, address: IPv4Address, port: int, user: str | None, protocol: str, readonly: bool = False) -> None:
        super().__init__(
            name=name,
            address=address,
            port=port,
            user=user,
            protocol=protocol,
            readonly=readonly,
            hypervisor='qemu'
        )
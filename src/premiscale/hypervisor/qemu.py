"""
Implement a Libvirt connection to a kvm-based hypervisor/host.
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

    def __init__(self, host: IPv4Address, port: int, user: str, auth_type: str, readonly: bool = False) -> None:
        super().__init__(host, port, user, 'qemu', auth_type, readonly)
"""
Implement a Libvirt connection to a kvm-based hypervisor/host.
"""


from premiscale.hypervisor._base import Libvirt


class Qemu(Libvirt):
    """
    Connect to a Qemu hypervisor.
    """
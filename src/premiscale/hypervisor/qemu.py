"""
Implement a Libvirt connection to a kvm-based hypervisor/host.
"""


from src.premiscale.hypervisor.libvirt import Libvirt


class Qemu(Libvirt):
    """
    Connect to a Qemu hypervisor.
    """
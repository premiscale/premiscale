"""
Implement a Libvirt connection to a kvm-based hypervisor/host.
"""


from premiscale.hypervisor.libvirt import Libvirt


class KVM(Libvirt):
    """
    Connect to a KVM hypervisor.
    """
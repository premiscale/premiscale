"""
Implement a Libvirt connection to a kvm-based hypervisor/host.
"""


from premiscale.hypervisor.libvirt import Libvirt


class ESX(Libvirt):
    """
    Connect to an ESX hypervisor.
    """
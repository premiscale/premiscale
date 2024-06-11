"""
Implement a Libvirt connection to a VMWare ESXi-based hypervisor/host.
"""


from premiscale.hypervisor._base import Libvirt


class VMware(Libvirt):
    """
    Connect to an ESXi hypervisor.
    """
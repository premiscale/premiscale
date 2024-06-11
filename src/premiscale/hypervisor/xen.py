"""
Implement a Libvirt connection to a Xen-based hypervisor/host.
"""


from premiscale.hypervisor._base import Libvirt


class Xen(Libvirt):
    """
    Connect to an Xen hypervisor.
    """
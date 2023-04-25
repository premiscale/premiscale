"""
Implement a Libvirt connection to a Xen-based hypervisor/host.
"""


from premiscale.hypervisor.libvirt import Libvirt


class Xen(Libvirt):
    """
    Connect to an Xen hypervisor.
    """
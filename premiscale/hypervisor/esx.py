"""
Implement a Libvirt connection to an ESX-based hypervisor/host.
"""


from premiscale.hypervisor.libvirt import Libvirt


class Esx(Libvirt):
    """
    Connect to an ESXi hypervisor.
    """
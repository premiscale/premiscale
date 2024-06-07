"""
Implement a Libvirt connection to an ESX-based hypervisor/host.
"""


from premiscale.hypervisor._base import Libvirt


class Esx(Libvirt):
    """
    Connect to an ESXi hypervisor.
    """
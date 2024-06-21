"""
Factory method for building hypervisor connections based on the user-provided configuration.
"""


from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from cattr import unstructure


if TYPE_CHECKING:
    from premiscale.hypervisor._base import Libvirt
    from premiscale.config.v1alpha1 import Host


log = logging.getLogger(__name__)


def build_hypervisor_connection(host: Host, readonly: bool = False) -> Libvirt:
    """
    Build a Libvirt connection object based on the user-provided configuration of the host.
    """
    conf = unstructure(host)

    # Remove the SSH key from the configuration as it's not needed for the connection.
    # It's only actually needed for the SSH config, which is parsed and produced when the config is validated.
    del conf['sshKey']

    match host.hypervisor:
        case 'qemu':
            log.debug(f'Using QEMU hypervisor for host {host.name} at {host.address}')

            from premiscale.hypervisor.qemu import Qemu

            # Subtypes don't need to know about the hypervisor type as it's already been set.
            del conf['hypervisor']

            return Qemu(
                readonly=readonly,
                **conf
            )
        # case 'esx':
        #     log.debug(f'Using ESX hypervisor for host {host.name} at {host.address}')

        #     from premiscale.hypervisor.esx import ESX

        #     del conf['hypervisor']

        #     return ESX(
        #         readonly=readonly,
        #         **conf
        #     )
        # case 'xen':
        #     log.debug(f'Using Xen hypervisor for host {host.name} at {host.address}')

        #     from premiscale.hypervisor.xen import Xen

        #     del conf['hypervisor']

        #     return Xen(
        #         readonly=readonly,
        #         **conf
        #     )
        case _:
            raise ValueError(f'Unknown hypervisor type: {host.hypervisor}')
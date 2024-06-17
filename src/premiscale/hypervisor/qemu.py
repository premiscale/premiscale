"""
Implement a Libvirt connection to a Qemu-based hypervisor/host.
"""


from __future__ import annotations

import logging
import re

from typing import TYPE_CHECKING
from libvirt import (
    libvirtError,
    # VIR_CONNECT_GET_ALL_DOMAINS_STATS_RUNNING,
    VIR_DOMAIN_RUNNING
)
from premiscale.hypervisor._base import Libvirt
from premiscale.hypervisor._schemas import DomainStats

if TYPE_CHECKING:
    from typing import Dict, List
    from ipaddress import IPv4Address


log = logging.getLogger(__name__)

NUMBER_REGEX = re.compile(r'(?<=_)\d+(?=_)')


class Qemu(Libvirt):
    """
    A subclass for interacting with a Qemu-based hypervisor/host.
    """

    def __init__(self,
                 name: str,
                 address: IPv4Address,
                 port: int,
                 protocol: str,
                 timeout: int = 60,
                 user: str | None = None,
                 readonly: bool = False,
                 resources: Dict | None = None) -> None:

        super().__init__(
            name=name,
            address=address,
            port=port,
            protocol=protocol,
            hypervisor='qemu',
            timeout=timeout,
            user=user,
            readonly=readonly,
            resources=resources
        )

    def getHostState(self) -> Dict:
        """
        Get the state of the VMs on the host.

        Returns:
            Dict: The state of the VMs on the host.
        """
        if self._connection is None:
            return {}

        domains = self._connection.listAllDomains()

        return {
            'virtualMachines': {
                vm.name(): vm.info() for vm in domains
            },

        }

    def getHostStats(self) -> Dict:
        """
        Get a report of schedulable resource utilization on the host.

        Returns:
            Dict: The resources available on the host.
        """
        if self._connection is None:
            return {}

        return {
            'hostStats': {
                'cpu': self._connection.getCPUStats(True),
                'memory': self._connection.getMemoryStats(-1, 0)
            }
        }

    def getHostVMStats(self) -> List[DomainStats]:
        """
        Get a report of resource utilization for a VM. A typical report includes all the following fields ~

            https://github.com/premiscale/premiscale/pull/196#issuecomment-2168388982

        And these fields are parsed into a DomainStats object.

        Returns:
            List[DomainStats]: Stats of all VMs on this particular host connection.
        """
        if self._connection is None:
            return []

        _all_domain_stats = self._connection.getAllDomainStats(
            # https://vscode.dev/github/premiscale/premiscale/blob/store-vm-dataremiscale/lib/python3.10/site-packages/libvirt.py#L6424-L6425
            # Using 0 for @stats returns all stats groups supported by the given hypervisor. See the link
            # above for an example of all the retrieved stats.
            stats=0,
            flags=VIR_DOMAIN_RUNNING
        )

        # Normalize domains' stat fields into a list of DomainStats objects.
        domain_stats_filtered_list: List[DomainStats] = []

        for (domain, stat) in _all_domain_stats:
            stat['name'] = domain.name()

            domain_keys = list(stat.keys())

            # Set up a bunch of empty iterables to store bins of parsed stats from this domain.
            # These will be unpacked into the DomainStats object.
            domain_stats_filtered = {}
            vcpus: List[Dict[str, int]] = []
            blocks: List[Dict[str, int]] = []
            nets: List[Dict[str, int]] = []

            # Normalize all the returned stats fields and parse them into a DomainStats object.
            for key in domain_keys:
                # Replace '-' and '.' with '_' in the keys for consistency.
                oldValue = stat.pop(key)
                key = key.replace('-', '_')
                key = key.replace('.', '_')
                stat[key] = oldValue

                # Bin parsed vCPU, Block, and Net stats to form the proper hierarchy.
                if key.startswith('vcpu_') and key != 'vcpu_current' and key != 'vcpu_maximum':
                    try:
                        index = int(key.split('_')[1])
                    except IndexError as e:
                        log.error(f'IndexError: {e}')
                        return []

                    vcpus.extend([{}] * (index - len(vcpus) + 1))

                    # Remove the number from the key and strip 'vcpu_' from the beginning.
                    _new_key = re.sub(NUMBER_REGEX, '', key).lstrip('vcpu_')

                    vcpus[index][_new_key] = stat[key]
                #
                elif key.startswith('block_') and key != 'block_count':
                    try:
                        index = int(key.split('_')[1])
                    except IndexError as e:
                        log.error(f'IndexError: {e}')
                        return []

                    blocks.extend([{}] * (index - len(blocks) + 1))

                    _new_key = re.sub(NUMBER_REGEX, '', key).lstrip('block_')

                    blocks[index][_new_key] = stat[key]
                #
                elif key.startswith('net_') and key != 'net_count':
                    try:
                        index = int(key.split('_')[1])
                    except IndexError as e:
                        log.error(f'IndexError: {e}')
                        return []

                    nets.extend([{}] * (index - len(nets) + 1))

                    _new_key = re.sub(NUMBER_REGEX, '', key).lstrip('net_')

                    nets[index][_new_key] = stat[key]
                else:
                    domain_stats_filtered[key] = stat[key]

            domain_stats_filtered[key] = stat[key]
            domain_stats_filtered['vcpu'] = vcpus
            domain_stats_filtered['block'] = blocks
            domain_stats_filtered['net'] = nets

            print(domain_stats_filtered)

            domain_stats_filtered_list.append(
                DomainStats(**domain_stats_filtered)
            )

        return domain_stats_filtered_list
"""
Implement a Libvirt connection to a Qemu-based hypervisor/host.

https://www.qemu.org/
"""


from __future__ import annotations

import logging
import re

from typing import TYPE_CHECKING, List, Tuple
from libvirt import (
    VIR_DOMAIN_NOSTATE,      # 0
    VIR_DOMAIN_RUNNING,      # 1
)
from xmltodict import parse as xmlparse
from cachetools import cached, TTLCache
from cattrs import structure
from premiscale.hypervisor._base import Libvirt, retry_libvirt_connection
from premiscale.hypervisor.qemu_data import DomainStats

if TYPE_CHECKING:
    from typing import Dict
    from ipaddress import IPv4Address


log = logging.getLogger(__name__)


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

    @cached(cache=TTLCache(maxsize=1, ttl=5))
    @retry_libvirt_connection()
    def _getHostStats(self) -> Dict:
        """
        Get a report of schedulable resource utilization on the host.

        Returns:
            Dict: The resources available on the host.
        """
        if self._connection is None:
            return {}

        _stats = {
            'host': {
                'name': self._connection.getHostname(),
                'type': self._connection.getType(),
                'uri': self._connection.getURI(),
                'version': self._connection.getVersion(),
                'libvirt_version': self._connection.getLibVersion(),
                'capabilities': xmlparse(self._connection.getCapabilities()),
                'node_info': self._connection.getInfo(),
                'max_vcpus': self._connection.getMaxVcpus(None),
                'free_memory': self._connection.getFreeMemory(),
                'node_memory': self._connection.getMemoryStats(-1, 0),
                'node_cpu_stats': self._connection.getCPUStats(True),
                'stats': {
                    'cpu': self._connection.getCPUStats(
                        cpuNum=-1,
                        flags=VIR_DOMAIN_NOSTATE
                    ),
                    'memory': self._connection.getMemoryStats(
                        cellNum=-1,
                        flags=VIR_DOMAIN_NOSTATE
                    )
                }
            },
            # Get a picture of the state of the host.
            'vms': [
                {
                    'name': vm.name(),
                    'state': vm.info()
                } for vm in self._connection.listAllDomains(flags=VIR_DOMAIN_NOSTATE)
            ]
        }

        return _stats

    @cached(cache=TTLCache(maxsize=1, ttl=5))
    @retry_libvirt_connection()
    def _getHostVMStats(self) -> List[DomainStats]:
        """
        Get a report of resource utilization for a VM. A typical report includes all the following fields ~

            https://github.com/premiscale/premiscale/pull/196#issuecomment-2168388982

        And these fields are parsed into a DomainStats object.

        Returns:
            List[DomainStats]: Stats of all VMs on this particular host connection.
        """

        MIDDLE_NUMBER_REGEX = re.compile(r'^(vcpu|block|net)_[0-9]+_')

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
                    _new_key = re.sub(MIDDLE_NUMBER_REGEX, '', key)

                    vcpus[index][_new_key] = stat[key]
                #
                elif key.startswith('block_') and key != 'block_count':
                    try:
                        index = int(key.split('_')[1])
                    except IndexError as e:
                        log.error(f'IndexError: {e}')
                        return []

                    blocks.extend([{}] * (index - len(blocks) + 1))

                    _new_key = re.sub(MIDDLE_NUMBER_REGEX, '', key)

                    blocks[index][_new_key] = stat[key]
                #
                elif key.startswith('net_') and key != 'net_count':
                    try:
                        index = int(key.split('_')[1])
                    except IndexError as e:
                        log.error(f'IndexError: {e}')
                        return []

                    nets.extend([{}] * (index - len(nets) + 1))

                    _new_key = re.sub(MIDDLE_NUMBER_REGEX, '', key)

                    nets[index][_new_key] = stat[key]
                else:
                    domain_stats_filtered[key] = stat[key]

            domain_stats_filtered['vcpu'] = vcpus
            domain_stats_filtered['block'] = blocks
            domain_stats_filtered['net'] = nets
            domain_stats_filtered['host'] = self.name
            domain_stats_filtered['address'] = self.address

            domain_stats_filtered_list.append(
                structure(domain_stats_filtered, DomainStats)
            )

        return domain_stats_filtered_list

    @cached(cache=TTLCache(maxsize=1, ttl=5))
    @retry_libvirt_connection()
    def statsToStateDB(self) -> List[Tuple]:
        """
        Convert the stats from the host into a state database entry. Instead of relying on the calling class to
        format these correctly, every interface is required to implement its own method to do so, since it's not
        guaranteed that the stats will be the same across different hypervisors.

        Returns:
            List[Tuple]: The state of the host and VMs on it.
        """
        return []

    @cached(cache=TTLCache(maxsize=1, ttl=5))
    @retry_libvirt_connection()
    def statsToMetricsDB(self) -> List[Tuple]:
        """
        Convert the stats from the host into a metrics database entry. Instead of relying on the calling class to
        format these correctly, every interface is required to implement its own method to do so, since it's not
        guaranteed that the stats will be the same across different hypervisors.

        Returns:
            List[Tuple]: Stats to a list of metrics database entries.
        """

        vm_stats: List[DomainStats] = self._getHostVMStats()

        log.debug(f'VM Stats for host {self.name}: {vm_stats}')

        # TODO: Implement a method to convert the host stats into a metrics database entry.
        host_stats: Dict = self._getHostStats()

        if vm_stats is None:
            return []

        tinyflux_vm_stats = [vm.to_tinyflux() for vm in vm_stats]

        return tinyflux_vm_stats
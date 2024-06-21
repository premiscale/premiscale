"""
Implement a Libvirt connection to a Qemu-based hypervisor/host.
"""


from __future__ import annotations

import logging
import re
import os

from attrs import define
from attr import ib
from typing import TYPE_CHECKING, List
from libvirt import (
    libvirtError,
    VIR_DOMAIN_NOSTATE,      # 0
    VIR_DOMAIN_RUNNING,      # 1
)
from xmltodict import parse as xmlparse
from cachetools import cached, TTLCache
from premiscale.hypervisor._base import Libvirt

if TYPE_CHECKING:
    from typing import Dict, Tuple
    from ipaddress import IPv4Address


log = logging.getLogger(__name__)

MIDDLE_NUMBER_REGEX = re.compile(r'(?<=_)[0-9]+(?=_)')


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
    def _getHostVMStats(self) -> List[DomainStats]:
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
                    _new_key = re.sub(MIDDLE_NUMBER_REGEX, '', key).lstrip('vcpu_')

                    vcpus[index][_new_key] = stat[key]
                #
                elif key.startswith('block_') and key != 'block_count':
                    try:
                        index = int(key.split('_')[1])
                    except IndexError as e:
                        log.error(f'IndexError: {e}')
                        return []

                    blocks.extend([{}] * (index - len(blocks) + 1))

                    _new_key = re.sub(MIDDLE_NUMBER_REGEX, '', key).lstrip('block_')

                    blocks[index][_new_key] = stat[key]
                #
                elif key.startswith('net_') and key != 'net_count':
                    try:
                        index = int(key.split('_')[1])
                    except IndexError as e:
                        log.error(f'IndexError: {e}')
                        return []

                    nets.extend([{}] * (index - len(nets) + 1))

                    _new_key = re.sub(MIDDLE_NUMBER_REGEX, '', key).lstrip('net_')

                    nets[index][_new_key] = stat[key]
                else:
                    domain_stats_filtered[key] = stat[key]

            domain_stats_filtered[key] = stat[key]
            domain_stats_filtered['vcpu'] = vcpus
            domain_stats_filtered['block'] = blocks
            domain_stats_filtered['net'] = nets

            domain_stats_filtered_list.append(
                DomainStats(**domain_stats_filtered)
            )

        return domain_stats_filtered_list

    def statsToStateDB(self) -> Dict:
        """
        Convert the stats from the host into a state database entry. Instead of relying on the calling class to
        format these correctly, every interface is required to implement its own method to do so, since it's not
        guaranteed that the stats will be the same across different hypervisors.
        """
        return {}

    def statsToMetricsDB(self) -> Dict:
        """
        Convert the stats from the host into a metrics database entry. Instead of relying on the calling class to
        format these correctly, every interface is required to implement its own method to do so, since it's not
        guaranteed that the stats will be the same across different hypervisors.
        """

        vm_stats: List[DomainStats] = self._getHostVMStats()
        host_stats: Dict = self._getHostStats()

        return {}


# Schemas for parsing retrieved hypervisor objects.

@define
class vCPU:
    """
    A dataclass for storing CPU statistics.
    """
    state: int
    time: int
    wait: int
    delay: int


@define
class Net:
    """
    A dataclass for storing network statistics.
    """
    name: str
    rx_bytes: int
    rx_pkts: int
    rx_errs: int
    rx_drop: int
    tx_bytes: int
    tx_pkts: int
    tx_errs: int
    tx_drop: int


@define
class Block:
    """
    A dataclass for storing block statistics.
    """
    name: str
    path: str
    backingIndex: int
    rd_reqs: int
    rd_bytes: int
    rd_times: int
    wr_reqs: int
    wr_bytes: int
    wr_times: int
    fl_reqs: int
    fl_times: int
    allocation: int
    capacity: int
    physical: int


@define
class DomainStats:
    """
    A dataclass for storing domain statistics. This is a normalized version of the stats returned by the libvirt API.

    This class also provides methods for converting the domain statistics into a compatible format for TinyFlux and InfluxDB.
    """
    name: str

    # State
    state_state: int
    state_reason: int

    # CPU
    cpu_time: int
    cpu_user: int
    cpu_system: int
    cpu_cache_monitor_count: int
    cpu_haltpoll_success_time: int
    cpu_haltpoll_fail_time: int

    balloon_rss: int

    # vCPU
    vcpu_current: int
    vcpu_maximum: int
    vcpu: List[vCPU]

    # net
    net: List[Net]

    # Block devices
    block: List[Block]
    dirtyrate_calc_status: int
    dirtyrate_calc_start_time: int
    dirtyrate_calc_period: int

    # Ballon fields with defaults (it doesn't seem every hypervisor will have these fields)
    balloon_current: int | None = ib(default=None)
    balloon_maximum: int | None = ib(default=None)
    balloon_swap_in: int | None = ib(default=None)
    balloon_swap_out: int | None = ib(default=None)
    balloon_major_fault: int | None = ib(default=None)
    balloon_minor_fault: int | None = ib(default=None)
    balloon_unused: int | None = ib(default=None)
    balloon_available: int | None = ib(default=None)
    balloon_usable: int | None = ib(default=None)
    balloon_last_update: int | None = ib(default=None)
    balloon_disk_caches: int | None = ib(default=None)
    balloon_hugetlb_pgalloc: int | None = ib(default=None)
    balloon_hugetlb_pgfail: int | None = ib(default=None)

    # Potentially dependent fields
    net_count: int | None = ib(default=None)
    block_count: int | None = ib(default=None)

    def __attrs_post_init__(self) -> None:
        if self.block_count is None:
            self.block_count = len(self.block)

        if self.net_count is None:
            self.net_count = len(self.net)

        if self.vcpu_current != self.vcpu_maximum:
            log.warning(f'vCPU count disparity for {self.name}: {self.vcpu_current} current != {self.vcpu_maximum} max. ')

    def to_tinyflux(self) -> Dict:
        """
        Convert the domain statistics into a compatible format for TinyFlux.

        Returns:
            Dict: all of the collected domain statistics with some additional fields.
        """
        return {
            'name': self.name,
            'state': {
                'state': self.state_state,
                'reason': self.state_reason
            },
            # Roughly speaking, these are the four main categories of stats we're interested in autoscaling virtual machines on.
            'cpu': {
                # Actual CPU utilization percentage is the difference between two consecutive differences between the total CPU
                # time and the sum of user and system time over some interval.
                'total_cpu_utilization': self.cpu_time - (self.cpu_user + self.cpu_system),
                'cpu_time': self.cpu_time,
                'cpu_user': self.cpu_user,
                'cpu_system': self.cpu_system,
                'vcpu_current': self.vcpu_current,
                'vcpu_maximum': self.vcpu_maximum
            },
            'memory': {
                # Memory utilization is the difference between the current and maximum balloon values.
                'total_memory_utilization': (self.balloon_current / self.balloon_maximum * 100 if self.balloon_current is not None and self.balloon_maximum is not None else -1),
            },
            'net': {
                'net_count': self.net_count,
                # Sum utilization, errors and drops across all network interfaces. We can use this to autoscale on network and
                # set thresholds for network errors and drops to either trigger a scale verb or affect scheduling of workloads.
                'total_net_utilization': sum(net.rx_bytes + net.tx_bytes for net in self.net),
                'total_net_errors': sum(net.rx_errs + net.tx_errs for net in self.net),
                'total_net_drops': sum(net.rx_drop + net.tx_drop for net in self.net),
                'net': [
                    {
                        'name': net.name,
                        # To autoscale on network interface utilization, we can use the sum of the rx_bytes and tx_bytes fields.
                        # This said, we don't know the % utilization of the physical NICs on the host from this metric. Virtual
                        # NICs are likely never going to be bottleneck intra-host, but physical NICs are.
                        'utilization': net.rx_bytes + net.tx_bytes,
                    } for net in self.net
                ]
            },
            'block': {
                'block_count': self.block_count,
                # Total physical allocation is the sum of all the physical block devices' 'block.physical' attributes.
                # This metric is grouped by block devices' mount points.
                # [
                #     {
                #         'mountpoint': '/var/lib/libvirt/images',
                #         'utilization': 159723239415
                #     },
                #     {
                #         'mountpoint': '/var/lib/libvirt/images2',
                #         'utilization': 159723239415
                #     }
                # ]
                # Later on, this metric can be used to determine the total physical allocation of a given mount point by VMs,
                # so scheduling can take this into account when placing VMs.
                'total_physical_allocation_bins': [
                    {
                        'mountpoint': mountpoint,
                        'utilization': sum(block.physical for block in self.block if os.path.dirname(block.path) == mountpoint)
                    } for mountpoint in set(os.path.dirname(block.path) for block in self.block)
                ],
                'block': [
                    {
                        'name': block.name,
                        # Capacity is the percentage of the block device that is currently being used.
                        'capacity_utilization': block.allocation / block.capacity * 100
                    } for block in self.block
                ]
            }
        }

    def to_influx(self) -> Dict:
        """
        Convert the domain statistics into a compatible format for InfluxDB.

        Returns:
            Dict: all of the collected domain statistics with some additional fields.

        Raises:
            NotImplementedError: This method has not been implemented yet.
        """
        raise NotImplementedError('This method has not been implemented yet.')


@define
class HostStats:
    """
    A dataclass for storing host time series metrics.
    """
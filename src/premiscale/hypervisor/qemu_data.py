"""
Implement a Libvirt connection to a Qemu-based hypervisor/host.
"""


from __future__ import annotations

import logging
import os

from attrs import define
from attr import ib
from cattr import structure
from typing import TYPE_CHECKING, List
from datetime import datetime, timezone

if TYPE_CHECKING:
    from typing import Dict, Tuple


log = logging.getLogger(__name__)


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
    A dataclass for storing network interface statistics.
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
    A dataclass for storing block device statistics.
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

    # Name and host are enough to uniquely identify a domain.
    name: str
    host: str
    address: str

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
    # TODO: https://github.com/python-attrs/attrs/issues/1298
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

    # Time of the collection. This is important for time series databases.
    time: datetime = ib(default=datetime.now(tz=timezone.utc))

    def __attrs_post_init__(self) -> None:
        if self.block_count is None:
            self.block_count = len(self.block)

        if self.net_count is None:
            self.net_count = len(self.net)

        if self.vcpu_current != self.vcpu_maximum:
            log.warning(f'vCPU count disparity for {self.name}: {self.vcpu_current} current != {self.vcpu_maximum} max. ')

    def to_tinyflux(self) -> Tuple[Dict, Dict, Dict, Dict]:
        """
        Convert the domain statistics into a compatible format for TinyFlux Point objects.

        In the process, 4 different points are created for the CPU, memory, network, and block device statistics.

        Block devices are a bit more complex than the other stats, so we'll break down the schema for them here.

        Block
        =====

            Total physical allocation is the sum of all the physical block devices' 'block.physical' attributes.
            This metric is grouped by block devices' mount points.

            Example:

                {
                    '/var/lib/libvirt/images_utilization': int,
                    '/var/lib/libvirt/images2_utilization': int
                }

            Later on, this metric can be used to determine the total physical allocation of a given mount point by VMs,
            so scheduling can take this into account when placing VMs.

        Returns:
            Tuple[Dict, Dict, Dict, Dict]: all of the concatenated domain statistics on which we can scale on with some
                additional fields. This object takes the following schema

            (
                {
                    # Name of the measurement. This is the name of the table in the database.
                    'measurement': str,

                    # Time of the measurement. It is important this data is stored alongside the collection time.
                    'time': datetime,

                    # Tag attributes that are searchable in the database
                    'tags': Dict[str, str],

                    # Actual data
                    'fields': Dict[str, int | float]
                },
                ... 4 times
            )
        """

        # Put together a record of the domain statistics that's palatable for TinyFlux.

        _cpu_datum: Dict = {
            'measurement': 'cpu',
            'time': self.time,
            'tags': {
                'name': self.name,
                'host': self.host,
                'state': str(self.state_state),
                'reason': str(self.state_reason)
            },
            'fields': {
                # Roughly speaking, these are the four main categories of stats we're interested in autoscaling virtual machines on.
                # Actual CPU utilization percentage is the difference between two consecutive differences between the total CPU time
                # and the sum of user and system time over some interval.
                # $\max(\frac{1}{I}\left(\frac{\text{cpu_time}_1 - (\text{cpu_user}_1 - \text{cpu_system}_1)}{\text{vcpu_current}_1}-\frac{\text{cpu_time}_2 - (\text{cpu_user}_2 - \text{cpu_system}_2)}{\text{vcpu_current}_2}\right), 0)
                'total_cpu_utilization': self.cpu_time - (self.cpu_user + self.cpu_system),
                'cpu_time': self.cpu_time,
                'cpu_user': self.cpu_user,
                'cpu_system': self.cpu_system,
                'vcpu_current': self.vcpu_current,
                'vcpu_maximum': self.vcpu_maximum,
            }
        }

        _memory_datum: Dict = {
            'measurement': 'memory',
            'time': self.time,
            'tags': {
                'name': self.name,
                'host': self.host,
                'state': str(self.state_state),
                'reason': str(self.state_reason)
            },
            'fields': {
                # Memory utilization is the difference between the current and maximum balloon values.
                'total_memory_utilization': round(self.balloon_current / self.balloon_maximum * 100, 2) if self.balloon_current is not None and self.balloon_maximum is not None else -1
            }
        }

        _net_datum: Dict = {
            'measurement': 'net',
            'time': self.time,
            'tags': {
                'name': self.name,
                'host': self.host,
                'state': str(self.state_state),
                'reason': str(self.state_reason)
            },
            'fields': {
                'net_count': self.net_count,
                # Sum utilization, errors and drops across all network interfaces. We can use this to autoscale on network and
                # set thresholds for network errors and drops to either trigger a scale verb or affect scheduling of workloads.
                'total_net_utilization': sum(net.rx_bytes + net.tx_bytes for net in self.net),
                'total_net_errors': sum(net.rx_errs + net.tx_errs for net in self.net),
                'total_net_drops': sum(net.rx_drop + net.tx_drop for net in self.net)
            }
        }

        # Calculate the utilization of each network interface.
        for net in self.net:
            # To autoscale on network interface utilization, we can use the sum of the rx_bytes and tx_bytes fields.
            # This said, we don't know the % utilization of the physical NICs on the host from this metric. Virtual
            # NICs are likely never going to be bottleneck intra-host, but physical NICs are.
            _net_datum['fields'][f'{net.name}_utilization'] = net.rx_bytes + net.tx_bytes

        _block_datum: Dict = {
            'measurement': 'block',
            'time': self.time,
            'tags': {
                'name': self.name,
                'host': self.host,
                'state': str(self.state_state),
                'reason': str(self.state_reason)
            },
            'fields': {
                'block_count': self.block_count
            }
        }

        # Calculate the capacity utilization of each block device.
        for block in self.block:
            _block_datum['fields'][f'{block.name}_capacity_utilization'] = round(block.allocation / block.capacity * 100, )

        for mountpoint in set(os.path.dirname(block.path) for block in self.block):
            _block_datum['fields'][f'{mountpoint}_utlization'] = sum(block.physical for _block in self.block if os.path.dirname(_block.path) == mountpoint)

        return (
            _cpu_datum,
            _memory_datum,
            _net_datum,
            _block_datum
        )

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
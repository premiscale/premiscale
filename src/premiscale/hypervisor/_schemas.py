"""
Provide dataclasses for parsing retrieved hypervisor objects.
"""


from __future__ import annotations

import logging

from attrs import define
from attr import ib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List


log = logging.getLogger(__name__)


## Domain statistics dataclasses


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
    A dataclass for storing domain statistics.
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


##
"""
Parse v1alpha1 configuration files into a Config object with attrs and cattrs.
"""


from __future__ import annotations

import logging
import os
import sys

from typing import TYPE_CHECKING
from attrs import define
from attr import ib
from cattrs import structure


if TYPE_CHECKING:
    from typing import List, Dict


log = logging.getLogger(__name__)


@define
class DatabaseCredentials:
    """
    Database credentials.
    """
    username: str
    password: str

    def __attrs_post_init__(self):
        """
        Post-initialization method to expand environment variables.
        """
        self.expand()

    def expand(self):
        """
        Expand environment variables in the database credentials.
        """
        self.username = os.path.expandvars(self.username)
        self.password = os.path.expandvars(self.password)


@define
class Connection:
    """
    Connection configuration options.
    """
    url: str
    database: str
    credentials: DatabaseCredentials

    def __attrs_post_init__(self):
        """
        Post-initialization method to expand environment variables.
        """
        self.expand()

    def expand(self):
        """
        Expand environment variables in the connection configuration.
        """
        self.url = os.path.expandvars(self.url)
        self.database = os.path.expandvars(self.database)


@define
class State:
    """
    State database configuration options.
    """
    type: str
    connection: Connection | None = ib(default=None)


@define
class TimeSeries:
    """
    Time series database configuration options.
    """
    type: str
    trailing: int
    connection: Connection | None = ib(default=None)


@define
class Databases:
    """
    Databases configuration options.
    """
    collectionInterval: int
    hostConnectionTimeout: int
    maxHostConnectionThreads: int
    state: State
    timeseries: TimeSeries


@define
class Certificates:
    """
    Certificate configuration options.
    """
    path: str

    def __attrs_post_init__(self):
        """
        Post-initialization method to expand environment variables.
        """
        self.expand()

    def expand(self):
        """
        Expand environment variables in the certificate configuration.
        """
        self.path = os.path.expandvars(self.path)


@define
class Platform:
    """
    Platform configuration options.
    """
    domain: str
    token: str
    certificates: Certificates
    actionsQueueMaxSize: int

    def __attrs_post_init__(self):
        """
        Post-initialization method to expand environment variables.
        """
        self.expand()

    def expand(self):
        """
        Expand environment variables in the platform configuration.
        """
        self.domain = os.path.expandvars(self.domain)
        self.token = os.path.expandvars(self.token)


@define
class Reconciliation:
    """
    Reconciliation configuration options.
    """
    interval: int


@define
class Resources:
    """
    Resource configuration options.
    """
    cpu: int
    memory: int


@define
class Host:
    """
    Host configuration options.
    """
    name: str
    address: str
    protocol: str
    port: int
    hypervisor: str
    resources: Resources | None = ib(default=None)


@define
class CloudInit:
    """
    Cloud-init configuration options.
    """
    user_data: str
    meta_data: str
    network_data: str
    vendor_data: str


@define
class HostReplacementStrategy:
    """
    Host replacement strategy configuration options.
    """
    strategy: str
    maxUnavailable: int
    maxSurge: int


@define
class Network:
    """
    Network configuration options.
    """
    dhcp: bool     # true, false
    gateway: str  # 192.168.1.1
    netmask: str  # 255.255.255.0
    subnet: str   # 192.168.1.0
    addressRange: str | None = ib(default=None) # e.g., if dhcp is true, '192.168.1.2-192.168.1.59'

    def __attrs_post_init__(self):
        """
        Post-initialization method to expand environment variables.
        """
        if self.dhcp and self.addressRange is None:
            log.error(f'Address range must be provided if DHCP is enabled.')
            sys.exit(1)


@define
class ScaleStrategy:
    """
    Scale strategy configuration options.
    """
    min: int
    max: int
    desired: int
    increment: int
    cooldown: int
    method: str
    targetUtilization: Dict[str, int]


@define
class AutoscalingGroup:
    """
    Autoscale group configuration options.
    """
    image: str
    domainName: str
    imageMigrationType: str
    cloudInit: CloudInit
    hosts: List[Host]
    replacement: HostReplacementStrategy
    networking: Network
    scaling: ScaleStrategy


@define(frozen=False)
class AutoscalingGroups:
    """
    Because keys are variable, we need to define a custom init method for autoscaling groups.
    """

    # https://www.attrs.org/en/stable/init.html#custom-init
    def __init__(self, **kwargs: Dict[str, AutoscalingGroup]):
        for key, value in kwargs.items():
            # This ends up being like,
            # asg_1: AutoscalingGroup
            # asg_2: AutoscalingGroup
            # etc. But we don't know how many ASGs users will configure so we can't statically type the keys.
            setattr(self, key, value)


@define
class Autoscale:
    """
    Autoscale configuration options.
    """
    hosts: List[Host]
    groups: AutoscalingGroups


@define
class Healthcheck:
    """
    Healthcheck configuration options.
    """
    host: str
    port: int

@define
class Controller:
    """
    Controller configuration options.
    """
    mode: str
    pidFile: str
    databases: Databases
    platform: Platform
    reconciliation: Reconciliation
    autoscale: Autoscale
    healthcheck: Healthcheck


@define
class Config:
    """
    Parse config files of version v1alpha1.
    """
    version: str
    controller: Controller

    @classmethod
    def from_dict(cls, config: dict) -> Config:
        """
        Create a Config object from a dictionary.

        Args:
            config (dict): The config dictionary.

        Returns:
            Config: The Config object.
        """
        return structure(
            config,
            cls
        )
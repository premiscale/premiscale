"""
Provide methods to interact with the Libvirt API.
"""


from __future__ import annotations

import libvirt as lv
import logging
import os

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from libvirt import libvirtError
from ipaddress import IPv4Address


if TYPE_CHECKING:
    from typing import Any, Dict


log = logging.getLogger(__name__)


class Libvirt(ABC):
    """
    Connect to hosts and provide an interface for interacting with VMs on them.

    Args:
        name (str): Name of the host.
        address (IPv4Address): IP address of the host to connect to.
        port (int): Port to connect to the host on.
        protocol (str): Type of authentication to use. Defaults to 'ssh'. Can be either 'ssh' or 'tls'.
        hypervisor (str): Type of hypervisor to connect to.
        timeout (int): Timeout for the connection. Defaults to 30 seconds.
        user (str | None): Username to authenticate with (if using SSH).
        readonly (bool): Whether to open the connection in read-only mode. Defaults to False.
        resources (Dict | None): Resources available on the host. Defaults to None.
    """
    def __init__(self,
                 name: str,
                 address: IPv4Address,
                 port: int,
                 protocol: str,
                 hypervisor: str,
                 timeout: int = 30,
                 user: str | None = None,
                 readonly: bool = False,
                 resources: Dict | None = None) -> None:
        self.name = name
        self.address = address
        self._address_str = str(address)
        self.port = port
        self.protocol = protocol
        self.timeout = timeout
        self.hypervisor = hypervisor

        # Set the user to 'root' if not provided by the end user.
        if user is None:
            self.user = 'root'
        else:
            self.user = user

        self.readonly = readonly
        self.resources = resources
        self._connection: lv.virConnect | None = None
        if protocol.lower() == 'ssh':
            # SSH
            self.connection_string = f'{hypervisor}+ssh://{user}@{address}:{port}/system'
        else:
            # TLS
            self.connection_string = f'{hypervisor}+tls://{address}:{port}/system'

    def __enter__(self) -> Libvirt | None:
        return self.open()

    def __exit__(self, *args: Any) -> None:
        self.close()

    def open(self) -> Libvirt | None:
        """
        Open a connection to the Libvirt hypervisor.
        """
        try:
            log.debug(f'Attempting to connect to host at {self.connection_string}')

            if self.readonly:
                self._connection = lv.openReadOnly(self.connection_string)
            else:
                self._connection = lv.open(self.connection_string)
                log.info(f'Connected to host at {self.connection_string}')
        except libvirtError as e:
            log.error(f'Failed to connect to host at {self.connection_string}: {e}')
            return None

        return self

    def close(self) -> None:
        """
        Close the connection with the Libvirt hypervisor.
        """
        if self._connection:
            self._connection.close()
            log.info(f'Closed connection to host at {self.connection_string}')
        else:
            log.error(f'No host connection to close, probably due to an error on connection open')

    @abstractmethod
    def getHostVMState(self) -> Dict:
        """
        Get the state of the VMs on the host.

        Returns:
            Dict: The state of the VMs on the host.
        """
        pass

    @abstractmethod
    def getHostSchedulableResourceUtilization(self) -> Dict:
        """
        Get a report of schedulable resource utilization on the host.

        Returns:
            Dict: The resources available on the host.
        """
        pass

    @abstractmethod
    def getVMResourceUtilization(self, vm_name: str) -> Dict:
        """
        Get a report of resource utilization for a VM.

        Args:
            vm_name (str): Name of the VM to get resource utilization for.

        Returns:
            Dict: The resources utilized by the VM.
        """
        pass
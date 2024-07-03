"""
Provide methods to interact with the Libvirt API.
"""


from __future__ import annotations

import libvirt as lv
import logging

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from libvirt import libvirtError
from functools import wraps


if TYPE_CHECKING:
    from ipaddress import IPv4Address
    from premiscale.hypervisor.qemu_data import DomainStats
    from typing import Any, Dict, List, Tuple, Callable


log = logging.getLogger(__name__)


def retry_libvirt_connection(retries: int = 3) -> Callable:
    """
    Decorator to retry a connection to the Libvirt hypervisor if it fails.

    Args:
        retries (int): Number of times to retry the connection. Defaults to 3.

    Returns:
        Callable: The decorated function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal retries

            self_ = args[0]
            assert isinstance(self_, Libvirt)
            tries = 0

            while tries < retries:
                try:
                    if self_.is_connected():
                        return func(*args, **kwargs)
                    else:
                        log.warning(f'Connection to host at "{self_.connection_string}" is not open, attempting to reconnect')
                        self_.open()
                        tries += 1
                        continue

                except libvirtError as e:
                    log.error(f'Failed to connect to host at "{self_.connection_string}" on try {tries + 1} / {retries}: {e}')
                    tries += 1

            log.error(f'Failed to connect to host at "{self_.connection_string}" after {retries} tries')

            return None
        return wrapper
    return decorator


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
            log.debug(f'Closed connection to host at {self.connection_string}')
        else:
            log.error(f'No host connection to close, probably due to an error on connection open')

    def is_connected(self) -> bool:
        """
        Check if the connection to the Libvirt hypervisor is open.

        Returns:
            bool: True if the connection is open.
        """
        return self._connection is not None

    @abstractmethod
    def _getHostStats(self) -> Dict:
        """
        Get a report of schedulable resource utilization on the host.

        Returns:
            Dict: The resources available on the host.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def _getHostVMStats(self) -> List[DomainStats]:
        """
        Get a report of resource utilization for a VM.

        Returns:
            List[DomainStats]: Stats of all VMs on this particular host connection.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def statsToStateDB(self) -> List[Tuple]:
        """
        Convert the stats from the host into a state database entry. Instead of relying on the calling class to
        format these correctly, every interface is required to implement its own method to do so, since it's not
        guaranteed that the stats will be the same across different hypervisors.

        Returns:
            List[Tuple]: The state of the host and VMs on it.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def statsToMetricsDB(self) -> List[Tuple]:
        """
        Convert the stats from the host into a metrics database entry. Instead of relying on the calling class to
        format these correctly, every interface is required to implement its own method to do so, since it's not
        guaranteed that the stats will be the same across different hypervisors.

        Returns:
            List[Tuple]: The metrics for the host and VMs on it.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError
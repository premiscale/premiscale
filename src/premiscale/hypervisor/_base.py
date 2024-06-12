"""
Provide methods to interact with the Libvirt API.
"""


from __future__ import annotations

import libvirt as lv
import logging
import os

from typing import TYPE_CHECKING
from libvirt import libvirtError
from ipaddress import IPv4Address


if TYPE_CHECKING:
    from typing import Any, Dict


log = logging.getLogger(__name__)


class Libvirt:
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
    def __init__(self, name: str, address: IPv4Address, port: int, protocol: str, hypervisor: str, timeout: int = 30, user: str | None = None, readonly: bool = False, resources: Dict | None = None) -> None:
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
            self._configure_ssh()
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
            self._connection.virConnectClose()
            log.info(f'Closed connection to host at {self.connection_string}')
        else:
            log.error(f'No host connection to close, probably due to an error on connection open.')

    def _configure_ssh(self) -> None:
        """
        Configure the SSH connection to the host. This method makes connection timeouts configurable.
        """
        with open(os.path.expanduser('~/.ssh/config'), mode='a+', encoding='utf-8') as ssh_config_f:
            ssh_config_f.seek(0)

            _conf = ssh_config_f.read().strip()

            if f'Host {self._address_str}' in _conf:
                log.debug(f'SSH connection to {self._address_str} already configured.')
                return None

            # Go to the end of the file.
            ssh_config_f.seek(
                0,
                os.SEEK_END
            )

            # Now write the new entry.
            if _conf == '':
                ssh_config_f.write(f'Host {self._address_str}\n  ConnectTimeout {self.timeout}\n')
            else:
                ssh_config_f.write(f'\nHost {self._address_str}\n  ConnectTimeout {self.timeout}\n')

        log.info(f'Configured SSH connection to {self._address_str} with a timeout of {self.timeout} seconds.')
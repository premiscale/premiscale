"""
Methods for interacting with the in-memory database.
"""


from __future__ import annotations

import logging
import sqlite3

from typing import TYPE_CHECKING
from wrapt import synchronized
from premiscale.metrics.state._base import State


if TYPE_CHECKING:
    from typing import List, Tuple


log = logging.getLogger(__name__)


class Local(State):
    """
    Implement a high-level interface to an in-memory state database.
    """

    def __init__(self) -> None:
        self._connection: sqlite3.Connection
        self._cursor: sqlite3.Cursor

    def is_connected(self) -> bool:
        """
        Check if the connection to the MySQL database is open.

        Returns:
            bool: True if the connection is open.
        """
        return self._connection is not None

    @synchronized
    def run(self, query: str, parameters: Tuple | None = None) -> List:
        """
        Run the in-memory database.
        """
        if parameters:
            q = self._cursor.execute(query, parameters).fetchall()
        else:
            q = self._cursor.execute(query).fetchall()

        self.commit()

        return q

    @synchronized
    def open(self, database: str = 'file::memory:?cache=shared') -> None:
        """
        Open a connection to a SQLite database. Defaults to an in-memory database.

        Args:
            database (str): Path to the SQLite database. Defaults to ':memory:'.
        """
        log.debug('Opening connection to in-memory SQLite database')
        self._connection = sqlite3.connect(
            database=database,
            check_same_thread=False
        )
        self._cursor = self._connection.cursor()
        log.debug('Connection to in-memory SQLite database opened')

    @synchronized
    def close(self) -> None:
        """
        Close the connection to the SQLite database.
        """
        log.debug('Closing connection to in-memory SQLite database')
        self._connection.close()

    @synchronized
    def commit(self) -> None:
        """
        Commit any changes to the SQLite database.
        """
        log.debug('Committing changes to in-memory SQLite database')
        self._connection.commit()

    @synchronized
    def rollback(self) -> None:
        """
        Rollback any changes to the SQLite database.
        """
        log.debug('Rolling back changes to in-memory SQLite database')
        self._connection.rollback()

    @synchronized
    def initialize(self) -> None:
        """
        Initialize the SQLite database.
        """
        log.debug('Initializing in-memory SQLite database')
        self._cursor.execute(
            'CREATE TABLE IF NOT EXISTS hosts (name TEXT, address TEXT, protocol TEXT, port INTEGER, hypervisor TEXT, cpu INTEGER, memory INTEGER, storage INTEGER)'
        )
        self._cursor.execute(
            'CREATE TABLE IF NOT EXISTS vms (host TEXT, name TEXT, cores INTEGER, memory INTEGER, storage INTEGER)'
        )
        self._cursor.execute(
            'CREATE TABLE IF NOT EXISTS asgs (name TEXT)'
        )
        self.commit()
        log.debug('In-memory SQLite database initialized')

    ## Hosts

    def get_host(self, name: str, address: str) -> Tuple | None:
        """
        Get a host record.

        Args:
            name (str): name of host to retrieve.
            address (str): IP address of the host.

        Returns:
            Tuple | None: Host record, if it exists. Otherwise, None.
        """
        entries = self._cursor.execute(
            'SELECT * FROM hosts WHERE name = ? AND address = ?',
            (name, address)
        ).fetchall()

        if len(entries) > 1:
            log.error(f'Expected 1 host record, got {len(entries)}. Returning the first entry.')
            log.debug(f'Host records: {entries}')
        elif len(entries) == 0:
            log.error('No host records found. Returning None.')
            return None

        return entries[0]

    @synchronized
    def host_create(self, name: str, address: str, protocol: str, port: int, hypervisor: str, cpu: int, memory: int, storage: int) -> bool:
        """
        Create a host record.

        Args:
            name (str): name to give host.
            address (str): IP address of the host.
            protocol (str): protocol to use for communication.
            port (int): port to communicate over.
            hypervisor (str): hypervisor to use for VM management.
            cpu (int): number of CPUs available.
            memory (int): amount of memory available.
            storage (int): amount of storage available.

        Returns:
            bool: True if action completed successfully.
        """
        self._cursor.execute(
            'INSERT INTO hosts (name, address, protocol, port, hypervisor, cpu, memory, storage) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (name, address, protocol, port, hypervisor, cpu, memory, storage)
        )
        self.commit()
        return True

    @synchronized
    def host_delete(self, name: str, address: str) -> bool:
        """
        Delete a host record.

        Args:
            name (str): name of host to delete the record for.
            address (str): IP address of the host.

        Returns:
            bool: True if action completed successfully.
        """
        self._cursor.execute(
            'DELETE FROM hosts WHERE name = ? AND address = ?',
            (name, address)
        )
        self.commit()
        return True

    @synchronized
    def host_update(self, name: str, address: str, protocol: str, port: int, hypervisor: str, cpu: int, memory: int, storage: int) -> bool:
        """
        Update a host record.

        Args:
            name (str): name to give host.
            address (str): IP address of the host.
            protocol (str): protocol to use for communication.
            port (int): port to communicate over.
            hypervisor (str): hypervisor to use for VM management.
            cpu (int): number of CPUs available.
            memory (int): amount of memory available.
            storage (int): amount of storage available.

        Returns:
            bool: True if action completed successfully.
        """
        self._cursor.execute(
            'UPDATE hosts SET protocol = ?, port = ?, hypervisor = ?, cpu = ?, memory = ?, storage = ? WHERE name = ? AND address = ?',
            (protocol, port, hypervisor, cpu, memory, storage, name, address)
        )
        self.commit()
        return True

    @synchronized
    def host_exists(self, name: str, address: str) -> bool:
        """
        Check if a host exists in the database.

        Args:
            name (str): name of host to check for.
            address (str): IP address of the host.

        Returns:
            bool: True if the host exists.
        """
        return self._cursor.execute(
            'SELECT * FROM hosts WHERE name = ? AND address = ?',
            (name, address)
        ).fetchone() is not None

    @synchronized
    def host_report(self) -> List:
        """
        Get a report of currently-managed hosts.

        Returns:
            List: List of hosts and the VMs on them.
        """
        return self._cursor.execute(
            'SELECT * FROM hosts'
        ).fetchall()

    ## VMs

    @synchronized
    def vm_create(self, host: str, vm_name: str, cores: int, memory: int, storage: int) -> bool:
        """
        Create a host record.

        Args:
            host (str): host on which to provision the VM.
            vm_name (str): name to give the new VM.
            cores (int): number of cores to allocate.
            memory (int): amount of memory to allocate.
            storage (int): amount of storage to allocate.

        Returns:
            bool: True if action completed successfully.
        """
        self._cursor.execute(
            'INSERT INTO vms (host, name, cores, memory, storage) VALUES (?, ?, ?, ?, ?)',
            (host, vm_name, cores, memory, storage)
        )
        self.commit()
        return True

    @synchronized
    def vm_delete(self, host: str, vm_name: str) -> bool:
        """
        Delete a VM on a specified host.

        Args:
            host (str): host on which to delete the VM.
            vm_name (str): name of VM to delete.

        Returns:
            bool: True if action completed successfully.
        """
        self._cursor.execute(
            'DELETE FROM vms WHERE host = ? AND name = ?',
            (host, vm_name)
        )
        self.commit()
        return True

    @synchronized
    def vm_report(self, host: str | None = None) -> List:
        """
        Get a report of VMs presently-managed on a host.

        Args:
            host (str | None): Name of host on which to retrieve VM entries. If None, return all VMs on all hosts. Defaults to None.

        Returns:
            List: List of VMs on the host, if host was specified; otherwise, all VMs on all hosts.
        """
        if host is None:
            return self._cursor.execute(
                'SELECT * FROM vms'
            ).fetchall()

        return self._cursor.execute(
            'SELECT * FROM vms WHERE host = ?',
            (host,)
        ).fetchall()

    ## ASGs

    @synchronized
    def asg_create(self, name: str) -> bool:
        """
        Create an autoscaling group.

        Args:
            name (str): Name to give the ASG.

        Returns:
            bool: True if action completed successfully.
        """
        self._cursor.execute(
            'INSERT INTO asgs (name) VALUES (?)',
            (name,)
        )
        self.commit()
        return True

    @synchronized
    def asg_delete(self, name: str) -> bool:
        """
        Delete an autoscaling group.

        Args:
            name (str): Name of ASG to delete.

        Returns:
            bool: True if action completed successfully.
        """
        self._cursor.execute(
            'DELETE FROM asgs WHERE name = ?',
            (name,)
        )
        self.commit()
        return True

    @synchronized
    def asg_add_vm(self, host: str, vm_name: str) -> bool:
        """
        Add a VM on a host to an autoscaling group.

        Args:
            host (str): Name of host on which the VM resides.
            vm_name (str): Name of VM to add to ASG.

        Returns:
            bool: True if action completed successfully.
        """
        self._cursor.execute(
            'INSERT INTO asgs (name) VALUES (?)',
            (vm_name,)
        )
        self.commit()
        return True

    @synchronized
    def asg_remove_vm(self, host: str, vm_name: str) -> bool:
        """
        Remove a VM on a host from an ASG.

        Args:
            host (str): Name of host on which the VM resides.
            vm_name (str): Name of VM to remove from ASG.

        Returns:
            bool: True if action completed successfully.
        """
        self._cursor.execute(
            'DELETE FROM asgs WHERE name = ?',
            (vm_name,)
        )
        self.commit()
        return True

    @synchronized
    def get_asg_vms(self, asg_name: str, host: str | None = None) -> List:
        """
        Get all VMs in an autoscaling group, optionally filtering by host.

        Args:
            asg_name (str): Name of ASG to retrieve VMs from.
            host (str | None): Optionally specify the name of host by which to filter the autoscaling group VMs by. Defaults to None.

        Returns:
            List: List of VMs in the ASG.
        """
        if host is None:
            return self._cursor.execute(
                'SELECT * FROM vms WHERE asg_name = ?',
                (asg_name,)
            ).fetchall()

        return self._cursor.execute(
            'SELECT * FROM vms WHERE name = ? AND host = ?',
            (asg_name, host)
        ).fetchall()

    @synchronized
    def asg_report(self, vm_enabled: bool = False) -> List:
        """
        Get a report of current autoscaling groups' standings. Optionally enable VMs be returned on hosts as well.

        Args:
            vm_enabled (bool, optional): Return VMs on hosts as well. Defaults to False as it's a more expensive operation.

        Returns:
            List: List of autoscaling groups and their VMs, if enabled
        """
        if vm_enabled:
            return self._cursor.execute(
                'SELECT * FROM asgs'
            ).fetchall()

        return self._cursor.execute(
            'SELECT * FROM asgs'
        ).fetchall()
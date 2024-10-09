"""
ABCs for state storage methods.
"""


from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod


if TYPE_CHECKING:
    from typing import Any, List, Tuple


log = logging.getLogger(__name__)


class State(ABC):
    """
    An abstract base class with a skeleton interface for state class types.
    """

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the connection to the MySQL database is open.

        Returns:
            bool: True if the connection is open.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def open(self) -> None:
        """
        Open a connection to the state backend these methods interact with.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """
        Close the connection to the state backend.

        This method should also dereference any secrets that may be stored in memory.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        """
        Commit any changes to the database.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the state backend.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def __enter__(self) -> State:
        self.open()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
        return

    ## Hosts

    @abstractmethod
    def get_host(self, name: str, address: str) -> Tuple | None:
        """
        Get a host record.

        Args:
            name (str): name of host to retrieve.
            address (str): IP address of the host.

        Returns:
            Tuple | None: Host record, if it exists. Otherwise, None.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
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

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def host_delete(self, name: str, address: str) -> bool:
        """
        Delete a host record.

        Args:
            name (str): name of host to delete the record for.
            address (str): IP address of the host.

        Returns:
            bool: True if action completed successfully.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
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

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def host_exists(self, name: str, address: str) -> bool:
        """
        Check if a host exists in the database.

        Args:
            name (str): name of host to check for.
            address (str): IP address of the host.

        Returns:
            bool: True if the host exists.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def host_report(self) -> List:
        """
        Get a report of currently-managed hosts.

        Returns:
            List: List of hosts and the VMs on them.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    ## VMs

    @abstractmethod
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

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def vm_delete(self, host: str, vm_name: str) -> bool:
        """
        Delete a VM on a specified host.

        Args:
            host (str): host on which to delete the VM.
            vm_name (str): name of VM to delete.

        Returns:
            bool: True if action completed successfully.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def vm_report(self, host: str | None = None) -> List:
        """
        Get a report of VMs presently-managed on a host.

        Args:
            host (str | None): Name of host on which to retrieve VM entries. If None, return all VMs on all hosts. Defaults to None.

        Returns:
            List: List of VMs on the host, or all VMs on all hosts if host is None.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    ## ASGs

    @abstractmethod
    def asg_create(self, name: str) -> bool:
        """
        Create an autoscaling group.

        Args:
            name (str): Name to give the ASG.

        Returns:
            bool: True if action completed successfully.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def asg_delete(self, name: str) -> bool:
        """
        Delete an autoscaling group.

        Args:
            name (str): Name of ASG to delete.

        Returns:
            bool: True if action completed successfully.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def asg_add_vm(self, host: str, vm_name: str) -> bool:
        """
        Add a VM on a host to an autoscaling group.

        Args:
            host (str): Name of host on which the VM resides.
            vm_name (str): Name of VM to add to ASG.

        Returns:
            bool: True if action completed successfully.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def asg_remove_vm(self, host: str, vm_name: str) -> bool:
        """
        Remove a VM on a host from an ASG.

        Args:
            host (str): Name of host on which the VM resides.
            vm_name (str): Name of VM to remove from ASG.

        Returns:
            bool: True if action completed successfully.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def get_asg_vms(self, name: str, host: str | None) -> List:
        """
        Get all VMs in an autoscaling group, optionally filtering by host.

        Args:
            name (str): Name of ASG to retrieve VMs from.
            host (str | None): Optionally specify the name of host by which to filter the autoscaling group VMs by.

        Returns:
            List: List of VMs in the ASG.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def asg_report(self, vm_enabled: bool = False) -> List:
        """
        Get a report of current autoscaling groups' standings. Optionally enable VMs be returned on hosts as well.

        Args:
            vm_enabled (bool, optional): Return VMs on hosts as well. Defaults to False as it's a more expensive operation.

        Returns:
            List: List of ASGs.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError
"""
Methods for interacting with the MySQL database.
"""

from typing import Any
from sqlalchemy.dialects.mysql import (
    insert,
)


url = 'mysql+mysqldb://<user>:<password>@<host>[:<port>]/<dbname>'


class MySQL:
    """
    Provide a clean interface to the MySQL database.
    """
    def __init__(self, url: str) -> None:
        self.url = url

    def __enter__(self) -> 'MySQL':
        return self

    def __exit__(self, *args: Any) -> None:
        return

    ## Hosts

    def host_create(self, hostname: str) -> bool:
        """
        Create a host record.

        Args:
            hostname (str): name to give host.

        Returns:
            bool: True if action completed successfully.
        """
        return True

    def host_delete(self, hostname: str) -> bool:
        """
        Delete a host record.

        Args:
            hostname (str): name of host to delete the record for.

        Returns:
            bool: True if action completed successfully.
        """
        return True

    def host_report(self) -> bool:
        """
        Get a report of currently-managed hosts.

        Returns:
            bool: True if action completed successfully.
        """
        return True

    ## VMs

    def vm_create(self, host: str, vm_name: str) -> bool:
        """
        Create a host record.

        Args:
            host (str): host on which to provision the VM.
            vm_name (str): name to give the new VM.

        Returns:
            bool: True if action completed successfully.
        """
        return True

    def vm_delete(self, host: str, vm_name: str) -> bool:
        """
        Delete a VM on a specified host.

        Args:
            host (str): host on which to delete the VM.
            vm_name (str): name of VM to delete.

        Returns:
            bool: True if action completed successfully.
        """
        return True

    def vm_report(self, host: str) -> bool:
        """
        Get a report of VMs presently-managed on a host.

        Args:
            host (str): Name of host on which to retrieve VM entries.

        Returns:
            bool: True if action completed successfully.
        """
        return True

    ## ASGs

    def asg_create(self, name: str) -> bool:
        """
        Create an autoscaling group.

        Args:
            name (str): Name to give the ASG.

        Returns:
            bool: True if action completed successfully.
        """
        return True

    def asg_delete(self, name: str) -> bool:
        """
        Delete an autoscaling group.

        Args:
            name (str): Name of ASG to delete.

        Returns:
            bool: True if action completed successfully.
        """
        return True

    def asg_add_vm(self, host: str, vm_name: str) -> bool:
        """
        Add a VM on a host to an autoscaling group.

        Args:
            host (str): Name of host on which the VM resides.
            vm_name (str): Name of VM to add to ASG.

        Returns:
            bool: True if action completed successfully.
        """
        return True

    def asg_remove_vm(self, host: str, vm_name: str) -> bool:
        """
        Remove a VM on a host from an ASG.

        Args:
            host (str): Name of host on which the VM resides.
            vm_name (str): Name of VM to remove from ASG.

        Returns:
            bool: True if action completed successfully.
        """
        return True

    def asg_report(self, vm_enabled: bool = False) -> bool:
        """
        Get a report of current autoscaling groups' standings. Optionally enable VMs be returned on hosts as well.

        Args:
            vm_enabled (bool, optional): Return VMs on hosts as well. Defaults to False as it's a more expensive operation.

        Returns:
            bool: True if action completed successfully.
        """
        return True
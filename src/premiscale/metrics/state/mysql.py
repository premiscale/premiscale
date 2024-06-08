"""
Methods for interacting with the MySQL database.
"""


from __future__ import annotations

import logging

from sqlmodel import Field, Session, SQLModel, create_engine
from premiscale.state._base import State


log = logging.getLogger(__name__)


class MySQL(State):
    """
    Provide a clean interface to the MySQL database.
    """
    def __init__(self, url: str, database: str, username: str, password: str) -> None:
        # url = 'mysql+mysqldb://<user>:<password>@<host>[:<port>]/<dbname>'
        self.url = url

        self.database = database
        self._username = username
        self._password = password
        self._connection = None

    def is_connected(self) -> bool:
        """
        Check if the connection to the MySQL database is open.

        Returns:
            bool: True if the connection is open.
        """
        return self._connection is not None

    def open(self) -> None:
        """
        Open a connection to the MySQL database.
        """
        # self.connection = mysql.connect(
        #     self._username,
        #     self._password,
        #     self.url,
        #     self.database
        # )
        self._username = ''
        self._password = ''

    def close(self) -> None:
        """
        Close the connection with the database.
        """
        # self._connection.close()

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
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

    def vm_create(self, hostname: str, vm_name: str) -> bool:
        """
        Create a host record.

        Args:
            hostname (str): host on which to provision the VM.
            vm_name (str): name to give the new VM.

        Returns:
            bool: True if action completed successfully.
        """
        return True

    def vm_delete(self, hostname: str, vm_name: str) -> bool:
        """
        Delete a VM on a specified host.

        Args:
            hostname (str): name to give host.

        Returns:
            bool: True if action completed successfully.
        """
        return True
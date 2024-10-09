"""
This module contains the models for the MySQL database. These models are automatically
created by SQLModel when the module is imported.
"""


from __future__ import annotations

import logging

from sqlmodel import Field, SQLModel


log = logging.getLogger(__name__)


class Host(SQLModel, table=True):
    """
    A model for the host table.
    """
    id: int = Field(primary_key=True)

    name: str = Field(index=True)
    address: str = Field(index=True)
    protocol: str
    port: int
    hypervisor: str
    cpu: int
    memory: int
    storage: int

    ipmi_address: str = Field(index=True)
    # This field is used to indicate whether or not the host is on.
    power: bool = Field(default=True)

    def equals(self, other: Host) -> bool:
        """
        Compares two Host objects to determine if they are equal.

        Args:
            other (Host): The other Host object to compare to.

        Returns:
            bool: True if the two Host objects are equal, False otherwise.
        """
        return self.name == other.name \
            and self.address == other.address \
            and self.protocol == other.protocol \
            and self.port == other.port \
            and self.hypervisor == other.hypervisor \
            and self.cpu == other.cpu \
            and self.memory == other.memory \
            and self.storage == other.storage \
            and self.power == other.power


class AutoScalingGroup(SQLModel, table=True):
    """
    A model for the auto scaling group table.
    """
    id: int = Field(primary_key=True)
    name: str = Field(index=True)
    domain_id: int = Field(foreign_key="domain.id")
    min_size: int
    max_size: int
    desired_capacity: int


class Domain(SQLModel, table=True):
    """
    A model for the domain table.
    """
    id: int = Field(primary_key=True)
    name: str = Field(index=True)
    host_id: int = Field(foreign_key="host.id")
    asg_id: int = Field(foreign_key="autoscalinggroup.id")
"""
Methods for interacting with the MySQL database.
"""


from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel
from premiscale.metrics.state._base import State

if TYPE_CHECKING:
    from typing import List, Tuple


log = logging.getLogger(__name__)


class Host(SQLModel, table=True):
    """
    A model for the host table.
    """
    id: int = Field(primary_key=True)
    name: str
    ip: str
    port: int
    username: str
    password: str
    power: bool


class Domain(SQLModel, table=True):
    """
    A model for the domain table.
    """
    id: int = Field(primary_key=True)
    name: str
    host_id: int = Field(foreign_key="host.id")
    asg_id: int = Field(foreign_key="auto_scaling_group.id")


class AutoScalingGroup(SQLModel, table=True):
    """
    A model for the auto scaling group table.
    """
    id: int = Field(primary_key=True)
    name: str
    domain_id: int
    min_size: int
    max_size: int
    desired_capacity: int
"""
Define actions the agent can take against infrastructure.
"""


from __future__ import annotations

import enum

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from premiscale.hypervisor._base import Libvirt


if TYPE_CHECKING:
    from typing import Any


class Verb(enum.Enum):
    """
    Classify different C[R]UD operations the controller can take on infrastructure, e.g. creating, deleting,
    or migrating VMs.
    """
    # Do nothing.
    NULL = 0

    # Creates
    CREATE = 1
    CLONE = 3

    # Updates
    MIGRATE = 2
    REPLACE = 4

    # Deletes
    DELETE = 10
    DELETE_STORAGE = 11


class Action(ABC):
    """
    Encapsulate the various actions that the autoscaler can take. These get queued up and acted upon in the
    autoscaling subprocess as threads. One action is processed at a time in each thread, and each thread
    corresponds to an ASG.
    """
    def __init__(self, action: Verb) -> None:
        self.action = action

    @abstractmethod
    def audit_trail_msg(self) -> dict:
        """
        Return a dictionary (JSON) object containing audit data about the action taken.

        Returns:
            dict: generates an audit trail message based on what occurred with the Action's execution.
        """
        return {}

    def kind(self) -> Verb:
        """
        Return the type of action.

        Returns:
            Verb: the type of action.
        """
        return self.action

    def __enter__(self) -> Action:
        return self

    def __exit__(self, *args: Any) -> None:
        pass


class Null(Action):
    """
    Action encapsulating logic to do nothing on a VM on a particular host.
    """
    def __init__(self, vm_name: str, host: str) -> None:
        super().__init__(action=Verb.NULL)


class Create(Action):
    """
    Action encapsulating logic to create a VM on a particular host.
    """
    def __init__(self, vm_name: str, host: str) -> None:
        super().__init__(action=Verb.CREATE)


class Migrate(Action):
    """
    Action encapsulating logic to migrate a VM from one host to another.
    """
    def __init__(self, vm_name: str, host: str) -> None:
        super().__init__(action=Verb.MIGRATE)
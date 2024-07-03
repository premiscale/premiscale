"""
Define actions the agent can take against infrastructure.
"""


from __future__ import annotations

from typing import TYPE_CHECKING
from attrs import define
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from premiscale.hypervisor._base import Libvirt
    from typing import Any


@define
class Verb:
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


class Action(ABC):
    """
    Encapsulate the various actions that the autoscaler can take. These get queued up and acted upon in the
    autoscaling subprocess as threads. One action is processed at a time in each thread, and each thread
    corresponds to an ASG.
    """
    def __init__(self, action: int) -> None:
        self.action = action

        # The number of virtual machines to act on.
        self.modifier = 0

    @abstractmethod
    def audit_trail_msg(self) -> dict:
        """
        Return a dictionary (JSON) object containing audit data about the action taken.

        Returns:
            dict: generates an audit trail message based on what occurred with the Action's execution.

        Raises:
            NotImplementedError: if the method is not implemented.
        """
        raise NotImplementedError

    def kind(self) -> int:
        """
        Return the type of action.

        Returns:
            int: the type of action.
        """
        return self.action

    def __enter__(self) -> Action:
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    @abstractmethod
    def __add__(self, other: Action) -> Action:
        """
        Add this action to another Action type.

        Args:
            other (Action): the other action to add to this one.

        Returns:
            Action: the action type that results from adding this action to the other action.

        Raises:
            NotImplementedError: if the method is not implemented.
        """
        raise NotImplementedError


class Null(Action):
    """
    Action encapsulating logic to do nothing on a VM on a particular host.
    """
    def __init__(self) -> None:
        self.modifier = 0
        super().__init__(action=Verb.NULL)

    def audit_trail_msg(self) -> dict:
        return {
            'action': 'null',
            'modifier': self.modifier
        }

    def __add__(self, other: Action) -> Action:
        """
        Add this action to another Action type.

        The Null action is like an identity action under addition; adding it to any other action will return the other action.

        Args:
            other (Action): the other action to add to this one.

        Returns:
            Action: the other action if it is not a Null action. Otherwise, returns this action.
        """
        if isinstance(other, Null):
            return self
        else:
            return other


class Create(Action):
    """
    Action encapsulating logic to create a VM on a particular host.
    """
    def __init__(self) -> None:
        super().__init__(action=Verb.CREATE)

    def audit_trail_msg(self) -> dict:
        """
        Return a dictionary (JSON) object containing audit data about the action taken.

        Returns:
            dict: an audit trail message based on what occurred with the Action's execution.
        """
        return {
            'action': 'create',
            'modifier': self.modifier
        }

    def __add__(self, other: Action) -> Action:
        """
        Add this action to another Action type.

        Args:
            other (Action): the other action to add to this one.

        Returns:
            Action: the action type that results from adding this action to the other action.
        """
        if isinstance(other, Create):
            act = Create()
            act.modifier = self.modifier + other.modifier
            return act
        # elif
        return other


class Migrate(Action):
    """
    Action encapsulating logic to migrate a VM from one host to another.
    """
    def __init__(self, vm_name: str, host: str) -> None:
        super().__init__(action=Verb.MIGRATE)


class Clone(Action):
    """
    Action encapsulating logic to clone a VM on a particular host.
    """
    def __init__(self, vm_name: str, host: str) -> None:
        super().__init__(action=Verb.CLONE)


class Replace(Action):
    """
    Action encapsulating logic to replace a VM on a particular host.
    """
    def __init__(self, vm_name: str, host: str) -> None:
        super().__init__(action=Verb.REPLACE)


class Delete(Action):
    """
    Action encapsulating logic to delete a VM on a particular host.
    """
    def __init__(self, vm_name: str, host: str) -> None:
        super().__init__(action=Verb.DELETE)
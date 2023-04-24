"""
Define actions the agent can take against infrastructure.
"""


import enum

from typing import Any
from premiscale.agent.libvirt import Libvirt


class Verb(enum.Enum):
    """
    Classify different actions the agent can take on infrastructure, e.g. creating, deleting, or migrating VMs.
    """
    # Creates
    CREATE = 1
    MIGRATE = 2
    CLONE = 3
    REPLACE = 4

    # Deletes
    DELETE = 10
    DELETE_STORAGE = 11


# Instances of Action are intended to execute in a thread on the ASG process.
class Action:
    """
    Encapsulate the various actions that the autoscaler can take. These get queued up and acted upon in the
    autoscaling daemon.
    """
    def __init__(self, action: Verb) -> None:
        self.action = action

    def audit_trail_msg(self) -> dict:
        """
        Return a dictionary (JSON) object containing audit data about the action taken.

        Returns:
            _type_: _description_
        """
        return {}

    def kind(self) -> Verb:
        """
        Return the type of action.

        Returns:
            str: _description_
        """
        return self.action

    def __enter__(self) -> Action:
        return self

    def __exit__(self, *args: Any) -> None:
        pass


class ActionCreate(Action):
    """
    Action encapsulating logic to create a VM on a particular host.
    """
    def __init__(self, vm_name: str, host: str) -> None:
        super().__init__(action=Verb.CREATE)
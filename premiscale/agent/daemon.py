"""
Define subprocesses encapsulating each control loop.
"""


from typing import Any

import logging
import asyncio
import signal
import sys
import websockets
import concurrent

from threading import Thread
from multiprocessing import Process, Queue
from daemon import DaemonContext, pidfile


log = logging.getLogger(__name__)


class Reconcile(Process):
    """
    Similar to metrics - a reconciliation loop that queries influxdb for the list of VMs
    metrics came from and compares these data to state stored in MySQL. If they don't match,
    actions to correct are added to the queue.
    """
    def __init__(self) -> None:
        pass


class Metrics(Process):
    """
    Handle metrics collection from hosts. Only one of these loops is created; metrics
    are published to influxdb for retrieval and query by the ASG loop, which evaluates
    on a per-ASG basis whether Actions need to be taken.
    """
    def __init__(self) -> None:
        pass


# Instances of Action are shorter-lived processes than the other 4.
class Action(Process):
    """
    Encapsulate the various actions that the autoscaler can take. These get queued up.
    """
    def __init__(self, typ: str) -> None:
        self.typ = typ

    def audit_trail_msg(self) -> dict:
        """
        Return a dictionary (JSON) object containing audit data about the action taken.

        Returns:
            _type_: _description_
        """
        return {}

    def get(self) -> str:
        """
        Return the type of action.

        Returns:
            str: _description_
        """
        return ''


class ASG(Process):
    """
    Handle actions. E.g., if a new VM needs to be created or deleted on some host,
    handle that action, and all relevant side-effects (e.g. updating MySQL state).

    One of these classes gets instantiated for every autoscaling group defined in
    the config.
    """
    def __init__(self) -> None:
        pass


class Platform(Process):
    """
    Handle communication to and from the platform. Maintains an async websocket
    connection and calls setters and getters on the other daemon threads' objects to
    configure them.
    """
    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.token = token
        self.websocket = None

    async def sync_actions(self) -> bool:
        """
        Sync actions taken by the agent for auditing.

        Returns:
            bool: True if the sync was successful.
        """
        return False

    async def sync_metrics(self) -> bool:
        """
        Sync metrics to the platform.

        Returns:
            bool: True if the sync was successful.
        """
        return False

    async def send_message(self, msg: str) -> bool:
        """
        Send an arbitrary message to the platform.

        Args:
            msg (str): Message to send.

        Returns:
            bool: True if the send was successful.
        """
        if not self.websocket:
            log.error('Cannot submit arbitrary message to platform, connection has not been established.')
            return False
        else:
            self.websocket.send(msg)

    async def set_up_connection(self) -> None:
        """
        Establish websocket connection to PremiScale's platform.
        """
        async with websockets.connect(self.url) as self.websocket:
            while True:
                try:
                    await asyncio.Future()
                except websockets.ConnectionClosed:
                    log.error(f'Websocket connection to {self.url} closed unexpectedly, reconnecting...')
                    continue

# Use this - https://docs.python.org/3.10/library/concurrent.futures.html?highlight=concurrent#processpoolexecutor
def wrapper(working_dir: str, pid_file: str, agent_config: dict, token: str = '') -> None:
    """
    Wrap our three daemon processes and pass along relevant data.

    Args:
        working_dir (str): working directory for this daemon.
        pid_file (str): PID file to use for the main daemon process.
        agent_config (dict): Agent config object.
        token (str): Agent registration token.
    """

    # We need one of these process trees for every ASG.

    autoscaling_action_queue: Queue = Queue()
    platform_message_queue: Queue = Queue()

    with concurrent.futures.Executor() as executor, DaemonContext(
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            detach_process=False,
            prevent_core=True,
            pidfile=pidfile.TimeoutPIDLockFile(pid_file),
            working_directory=working_dir,
            signal_map={
                signal.SIGTERM: executor.shutdown,
                signal.SIGHUP: executor.shutdown,
                signal.SIGINT: executor.shutdown,
            }
        ):
        ...
        # executor.submit(Platform, platform_message_queue)
        # executor.submit(ASG, autoscaling_action_queue)
        # executor.submit(Metrics)
        # executor.submit(Reconcile, autoscaling_action_queue, platform_message_queue)
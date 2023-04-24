"""
Define subprocesses encapsulating each control loop.
"""


from typing import Dict

import logging
import asyncio
import signal
import sys
import websockets
import concurrent

from multiprocessing import Queue
from daemon import DaemonContext, pidfile

from premiscale.config._config import Config
from premiscale.agent.actions import Action, Verb


log = logging.getLogger(__name__)


class Reconcile:
    """
    Similar to metrics - a reconciliation loop that queries influxdb for the list of VMs
    metrics came from and compares these data to state stored in MySQL. If they don't match,
    actions to correct the state drift are added to the queue.
    """
    def __init__(self, state_connection: dict, metrics_connection: dict) -> None:
        match state_connection['type']:
            case 'mysql':
                from premiscale.state.mysql import MySQL
                del(state_connection['type'])
                self.state_database = MySQL(**state_connection)

        match metrics_connection['type']:
            case 'influxdb':
                from premiscale.metrics.influxdb import InfluxDB
                del(metrics_connection['type'])
                self.metrics_database = InfluxDB(**metrics_connection)

        self.platform_queue: Queue
        self.asg_queue: Queue

    def __call__(self, asg_queue: Queue, platform_queue: Queue) -> None:
        self.asg_queue = asg_queue
        self.platform_queue = platform_queue


class Metrics:
    """
    Handle metrics collection from hosts. Only one of these loops is created; metrics
    are published to influxdb for retrieval and query by the ASG loop, which evaluates
    on a per-ASG basis whether Actions need to be taken.
    """
    def __init__(self, connection: dict) -> None:
        match connection['type']:
            case 'influxdb':
                from premiscale.metrics.influxdb import InfluxDB
                del(connection['type'])
                self.metrics_database = InfluxDB(**connection)

    def __call__(self) -> None:
        pass


class ASG:
    """
    Handle actions. E.g., if a new VM needs to be created or deleted on some host,
    handle that action, and all relevant side-effects (e.g. updating MySQL state).

    One of these classes gets instantiated for every autoscaling group defined in
    the config.
    """
    def __init__(self) -> None:
        self.queue: Queue

    def __call__(self, asg_queue: Queue) -> None:
        self.queue = asg_queue


class Platform:
    """
    Handle communication to and from the platform. Maintains an async websocket
    connection and calls setters and getters on the other daemon threads' objects to
    configure them.
    """
    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.websocket = None
        self.queue: Queue
        self._register(token)
        self.auth: Dict = {}

    def _register(self, token: str) -> None:
        """
        Register the agent with the platform.
        """

    def __call__(self, platform_queue: Queue) -> None:
        self.queue = platform_queue

        # This should never exit. Process should stay open forever.
        asyncio.run(self.set_up_connection())

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
def wrapper(working_dir: str, pid_file: str, agent_config: Config, token: str = '', host: str = '') -> None:
    """
    Wrap our four daemon processes and pass along relevant data.

    Args:
        working_dir (str): working directory for this daemon.
        pid_file (str): PID file to use for the main daemon process.
        agent_config (Config): Agent config object.
        token (str): Agent registration token.
        host (str): PremiScale platform host.
    """

    # We need one of these process trees for every ASG.

    autoscaling_action_queue: Queue = Queue()
    platform_message_queue: Queue = Queue()

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor, DaemonContext(
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

        platform_future: concurrent.futures.Future = executor.submit(
            Platform(host, token),
            platform_message_queue
        )

        asg_future: concurrent.futures.Future = executor.submit(
            ASG(),
            autoscaling_action_queue
        )

        metrics_future: concurrent.futures.Future = executor.submit(
            Metrics(
                agent_config.agent_databases_metrics_connection() # type: ignore
            )
        )

        reconciliation_future: concurrent.futures.Future = executor.submit(
            Reconcile(
                agent_config.agent_databases_state_connection(), # type: ignore
                agent_config.agent_databases_metrics_connection() # type: ignore
            ),
            autoscaling_action_queue,
            platform_message_queue
        )
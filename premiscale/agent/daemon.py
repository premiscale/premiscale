"""
Define subprocesses encapsulating each control loop.
"""


import multiprocessing as mp
import logging
import asyncio
# import signal
# import sys
import websockets as ws
import concurrent
import time
import socket

from urllib.parse import urljoin
from multiprocessing.queues import Queue
from typing import Dict, cast
# from daemon import DaemonContext, pidfile

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
        log.debug('Starting reconciliation subprocess')
        while True:
            self.platform_queue.put('Hello')
            time.sleep(5)
        # Open database connections


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
        log.debug('Starting metrics collection subprocess')


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
        log.debug('Starting autoscaling subprocess')


class Platform:
    """
    Handle communication to and from the platform. Maintains an async websocket
    connection and calls setters and getters on the other daemon threads' objects to
    configure them.
    """
    def __init__(self, url: str, token: str, path: str = '/agent/websocket') -> None:
        # Path needs to align with the Helm chart's ingress.
        self.url = urljoin(url, path)
        self.websocket = None
        self.queue: Queue
        self._auth: Dict = dict()
        self._register(token)

    def _register(self, token: str) -> None:
        """
        Register the agent with the platform.
        """

    def __call__(self, platform_queue: Queue) -> None:
        self.queue = platform_queue
        log.debug('Starting platform connection subprocess')
        # This should never exit. Process should stay open forever.
        asyncio.run(self._set_up_connection())

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

    async def send_message(self, msg: str) -> None:
        """
        Send an arbitrary message to the platform.

        Args:
            msg (str): Message to send.

        Returns:
            bool: True if the send was successful.
        """
        if not self.websocket:
            log.error('Cannot submit arbitrary message to platform, connection has not been established.')
        else:
            await self.websocket.send(msg)

    async def _sync_platform_queue(self) -> None:
        """
        Sync the platform queue with the platform. If this function returns, then the queue is empty.
        """
        # Clear the queue.
        while (msg := self.queue.get()) is not None:
            await self.send_message(msg)
        else:
            await self.send_message('')

    async def _set_up_connection(self) -> None:
        """
        Establish websocket connection to PremiScale's platform.
        """
        while True:
            try:
                async with ws.connect(self.url) as self.websocket:
                    try:
                        log.info(f'Established connection to platform hosted at \'{self.url}\'')
                        while True:
                            await self._sync_platform_queue()
                            time.sleep(5)
                        # await asyncio.Future()
                    except ws.ConnectionClosed:
                        log.error(f'Websocket connection to \'{self.url}\' closed unexpectedly, reconnecting...')
                        continue
            except socket.gaierror as msg:
                log.error(f'Could not connect to \'{self.url}\', retrying: {msg}')
                time.sleep(1)
                continue

# Use this - https://docs.python.org/3.10/library/concurrent.futures.html?highlight=concurrent#processpoolexecutor
def start(working_dir: str, pid_file: str, agent_config: Config, token: str, host: str) -> None:
    """
    Start our four daemon processes passing along relevant configuration.

    Args:
        working_dir (str): working directory for this daemon.
        pid_file (str): PID file to use for the main daemon process.
        agent_config (Config): Agent config object.
        token (str): Agent registration token.
        host (str): PremiScale platform host.
    """
    # mp.set_start_method('spawn')

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor, mp.Manager() as manager:
        # DaemonContext(
        #     stdin=sys.stdin,
        #     stdout=sys.stdout,
        #     stderr=sys.stderr,
        #     # files_preserve=[],
        #     detach_process=False,
        #     prevent_core=True,
        #     pidfile=pidfile.TimeoutPIDLockFile(pid_file),
        #     working_directory=working_dir,
        #     signal_map={
        #         signal.SIGTERM: executor.shutdown,
        #         signal.SIGHUP: executor.shutdown,
        #         signal.SIGINT: executor.shutdown,
        #     }
        # ):

        autoscaling_action_queue: Queue = cast(Queue, manager.Queue())
        platform_message_queue: Queue = cast(Queue, manager.Queue())

        processes = [
            # Platform websocket connection subprocess (maintains connection and data stream -> premiscale platform).
            # If no registration token or platform host is provided, this process is not spawned.
            executor.submit(
                Platform(host, token),
                platform_message_queue
            ) if token and host else None,
            # Autoscaling controller subprocess (works on Actions in the ASG queue)
            executor.submit(
                ASG(),
                autoscaling_action_queue
            ),
            # Host metrics collection subprocess (populates metrics database)
            executor.submit(
                Metrics(
                    agent_config.agent_databases_metrics_connection() # type: ignore
                )
            ),
            # Metrics <-> state database reconciliation subprocess (creates actions on the ASGs queue)
            executor.submit(
                Reconcile(
                    agent_config.agent_databases_state_connection(), # type: ignore
                    agent_config.agent_databases_metrics_connection() # type: ignore
                ),
                autoscaling_action_queue,
                platform_message_queue
            )
        ]

        for process in processes:
            if process is not None:
                process.result()
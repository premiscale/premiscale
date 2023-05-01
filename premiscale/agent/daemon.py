"""
Define subprocesses encapsulating each control loop.
"""


import multiprocessing as mp
import logging
# import signal
# import sys
import concurrent

from multiprocessing.queues import Queue
from typing import cast
from setproctitle import setproctitle
# from daemon import DaemonContext, pidfile
from premiscale.config._config import Config
from premiscale.agent.platform import Platform, register
from premiscale.agent.autoscaling import ASG
from premiscale.agent.metrics import Metrics
from premiscale.agent.reconciliation import Reconcile


log = logging.getLogger(__name__)


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
    setproctitle('premiscale')

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
            # Platform websocket connection subprocess. Maintains connection and data stream -> premiscale platform).
            # If either the (1) registration token or (2) platform host isn't provided, this process is not spawned.
            executor.submit(
                Platform(host, token),
                platform_message_queue
            ) if register(token, f'https://{host}', 'agent/registration') else None,
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
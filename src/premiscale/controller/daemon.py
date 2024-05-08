"""
Define subprocesses encapsulating each control loop.
"""


import multiprocessing as mp
import logging
import signal
import sys
import concurrent
import os

from multiprocessing.queues import Queue
from typing import cast
from setproctitle import setproctitle
from daemon import DaemonContext, pidfile

from premiscale.config._config import Config
from premiscale.controller.platform import Platform, register
from premiscale.controller.autoscaling import ASG
from premiscale.controller.metrics import Metrics
from premiscale.controller.reconciliation import Reconcile
from premiscale.api.healthcheck import (
    Healthcheck,
    api as healthcheck_api
)


log = logging.getLogger(__name__)


def start(
        working_dir: str,
        pid_file: str,
        agent_config: Config,
        agent_version: str,
        token: str,
        host: str,
        cacert: str
    ) -> int:
    """
    Start our four daemon processes passing along relevant configuration.

    Args:
        working_dir (str): working directory for this daemon.
        pid_file (str): PID file to use for the main daemon process.
        agent_config (Config): Agent config object.
        agent_version (str): Agent version (from the package metadata).
        token (str): Agent registration token.
        host (str): PremiScale platform host.
        cacert (str): Path to the certificate file (for use with self-signed certificates).

    Returns:
        int: return code.
    """
    setproctitle('premiscale')

    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor, mp.Manager() as manager:
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
            # Platform websocket connection subprocess. Maintains registration, connection and data stream -> premiscale platform).
            executor.submit(
                Platform(
                    registration=registration,
                    version=agent_version,
                    host=f'wss://{host}',
                    path='agent/websocket',
                    cacert=cacert
                ),
                platform_message_queue
            ) if (registration := register(
                token=token,
                version=agent_version,
                host=f'https://{host}',
                path='agent/registration',
                cacert=cacert
            )) else None,

            # Healthcheck subprocess (serves healthcheck endpoint in Docker containers).
            executor.submit(
                Healthcheck(
                    options={
                        'bind': 'localhost:8080',
                        'workers': 1,
                        'backlog': 10,
                        'worker_class': 'sync',
                        'worker_connections': 10,
                        'timeout': 10,
                        'keepalive': 5,
                        'spew': False,
                        'daemon': False,
                        'raw_env': [],
                        'pidfile': None,
                        'umask': 0,
                        'user': None,
                        'group': None,
                        'tmp_upload_dir': None,
                        'errorlog': '-',
                        'loglevel': 'info',
                        'accesslog': '-',
                        'access_log_format': '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"',
                        'proc_name': 'healthcheck'
                    },
                    app=healthcheck_api
                ).run,
            ) if os.getenv('IN_DOCKER') else None,

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

    return 0
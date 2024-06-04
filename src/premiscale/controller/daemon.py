"""
Define subprocesses encapsulating each control loop.
"""


import concurrent.futures
import multiprocessing as mp
import logging
import signal
import sys
import concurrent
import os
import threading

from functools import partial
from multiprocessing.queues import Queue
from typing import cast
from setproctitle import setproctitle
from daemon import DaemonContext, pidfile

from premiscale.config.v1alpha1 import Config
from premiscale.controller.platform import Platform, register
from premiscale.controller.autoscaling import ASG
from premiscale.controller.metrics import Metrics
from premiscale.controller.reconciliation import Reconcile
from premiscale.healthcheck import app as healthcheck


log = logging.getLogger(__name__)


def start(
        working_dir: str,
        controller_config: Config,
        controller_version: str,
        token: str
    ) -> int:
    """
    Start our four daemon processes passing along relevant configuration.

    Args:
        working_dir (str): the working directory of the daemon context.
        controller_config (Config): 

    Returns:
        int: return code.
    """
    setproctitle('premiscale')

    # Start the healthcheck API in a separate thread off our main process as a daemon.
    _main_process_threads = [
        threading.Thread(
            target=partial(
                healthcheck.run,
                host='127.0.0.1',
                port=8085,
                debug=True,
                use_reloader=False
            ),
            daemon=True
        ),
    ]

    for thread in _main_process_threads:
        thread.start()

    with concurrent.futures.ProcessPoolExecutor() as executor, mp.Manager() as manager:
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
                    version=controller_version,
                    host=f'wss://{platform}',
                    path='agent/websocket',
                    cacert=cacert
                ),
                platform_message_queue
            ) if (registration := register(
                token=token,
                version=controller_version,
                host=f'https://{platform}',
                path='agent/registration',
                cacert=cacert
            )) else None,

            # Autoscaling controller subprocess (works on Actions in the ASG queue)
            executor.submit(
                ASG(),
                autoscaling_action_queue
            ),

            # Host metrics collection subprocess (populates metrics database)
            executor.submit(
                Metrics(
                    controller_config.controller_databases_metrics_connection() # type: ignore
                )
            ),

            # Metrics <-> state database reconciliation subprocess (creates actions on the ASGs queue)
            executor.submit(
                Reconcile(
                    controller_config.controller_databases_state_connection(), # type: ignore
                    controller_config.controller_databases_metrics_connection() # type: ignore
                ),
                autoscaling_action_queue,
                platform_message_queue
            )
        ]

        for process in processes:
            if process is not None:
                process.result()

    for thread in _main_process_threads:
        thread.join()

    return 0
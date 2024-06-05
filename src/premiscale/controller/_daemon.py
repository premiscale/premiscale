"""
Define subprocesses and any main-process threads for the controller.
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
from premiscale.controller.platform import Platform
from premiscale.controller.autoscaling import ASG
from premiscale.controller.metrics import MetricsCollector
from premiscale.controller.reconciliation import Reconcile
from premiscale.healthcheck import app as healthcheck


log = logging.getLogger(__name__)


def start(
        config: Config,
        version: str,
        token: str
    ) -> int:
    """
    Start our subprocesses and the healthcheck API for Docker and Kubernetes.

    Args:
        config (Config): controller config file as a Config object.
        version (str): controller version.
        token (str): controller registration token.

    Returns:
        int: status code of the first subprocess to exit.
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

    with concurrent.futures.ProcessPoolExecutor() as executor, mp.Manager() as manager:
        # DaemonContext(
        #     stdin=sys.stdin,
        #     stdout=sys.stdout,
        #     stderr=sys.stderr,
        #     # files_preserve=[],
        #     detach_process=False,
        #     prevent_core=True,
        #     pidfile=pidfile.TimeoutPIDLockFile(pid_file),
        #     working_directory=os.getenv('HOME'),
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
                Platform.register(
                    version=version,
                    token=token,
                    host=config.controller.platform.domain,
                    websocket_path='agent/websocket',
                    registration_path='agent/register',
                    cacert=config.controller.platform.certificates.path
                ),
                platform_message_queue
            ),

            # Autoscaling controller subprocess (works on Actions in the ASG queue)
            executor.submit(
                ASG(config),
                autoscaling_action_queue
            ),

            # Host metrics collection subprocess (populates metrics database)
            executor.submit(
                MetricsCollector(config)
            ),

            # Metrics <-> state database reconciliation subprocess (creates actions on the ASGs queue)
            executor.submit(
                Reconcile(config),
                autoscaling_action_queue,
                platform_message_queue
            )
        ]

        for _dthread in _main_process_threads:
            _dthread.start()

        for process in processes:
            if process is not None:
                process.result()

    for thread in _main_process_threads:
        thread.join()

    return 0
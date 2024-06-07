"""
This module is responsible for starting relevant subprocesses and main-process threads based on how the
controller is configured. It also starts the healthcheck API for Docker and Kubernetes.
"""


import multiprocessing as mp
import logging
# import signal
# import sys
# import os

from functools import partial
from multiprocessing.queues import Queue
from concurrent.futures import ProcessPoolExecutor
from threading import Thread
from typing import cast
from setproctitle import setproctitle
# from daemon import DaemonContext, pidfile
from premiscale.config.v1alpha1 import Config
from premiscale.controller.reconciliation import Reconcile
from premiscale.api.healthcheck import app as healthcheck
from premiscale.autoscaling import ASG
from premiscale.platform import Platform


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
    _main_process_daemon_threads = [
        Thread(
            target=partial(
                healthcheck.run,
                host=config.controller.healthcheck.host,
                port=config.controller.healthcheck.port,
                debug=True,
                use_reloader=False
            ),
            daemon=True
        ),
    ]

    with ProcessPoolExecutor() as executor, mp.Manager() as manager:
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

        # Submit the core PremiScale subprocesses that don't depend on the controller mode.
        processes = [
            # Platform websocket connection subprocess. Maintains registration, connection and data stream -> premiscale platform).
            executor.submit(
                Platform.register(
                    version=version,
                    token=token,
                    host=config.controller.platform.domain,
                    cacert=config.controller.platform.certificates.path
                ),
                platform_message_queue
            ),

            # Autoscaling controller subprocess (works on Actions in the ASG queue)
            executor.submit(
                ASG(config),
                autoscaling_action_queue
            ),
            # Metrics <-> state database reconciliation subprocess (creates actions on the ASGs queue)
            executor.submit(
                Reconcile(config),
                autoscaling_action_queue,
                platform_message_queue
            )
        ]

        # Based on the mode the controller was started in (Kubernetes or standalone), we start the relevant subprocesses.
        match config.controller.mode:
            case 'kubernetes':
                from premiscale.kubernetes import KubernetesAutoscaler

                # Collect metrics from the Kubernetes autoscaler and translate them into PremiScale Actions for
                # the Autoscaling subprocess to process.
                processes.append(
                    executor.submit(
                        KubernetesAutoscaler(config),
                        autoscaling_action_queue
                    )
                )
            case 'standalone':
                # Host metrics collection subprocess (populates metrics database)
                from premiscale.metrics import build_metrics

                processes.append(
                    executor.submit(
                        build_metrics(config)
                    )
                )


        for _dthread in _main_process_daemon_threads:
            _dthread.start()

        for process in processes:
            if process is not None:
                process.result()

    # TODO: send Event to indicate that the thread should exit.
    for thread in _main_process_daemon_threads:
        thread.join()

    return 0
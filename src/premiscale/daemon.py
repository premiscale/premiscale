"""
This module is responsible for starting relevant subprocesses and main-process threads based on how the
controller is configured. It also starts the healthcheck API for Docker and Kubernetes.
"""


from __future__ import annotations

import multiprocessing as mp
import logging
import traceback

from functools import partial
from multiprocessing.queues import Queue
from concurrent.futures import ProcessPoolExecutor, as_completed
from threading import Thread
from typing import cast, TYPE_CHECKING
from setproctitle import setproctitle
from premiscale.api.healthcheck import app as healthcheck
from premiscale.autoscaling.group import Autoscaler
from premiscale.platform import Platform
from premiscale.metrics import MetricsCollector


if TYPE_CHECKING:
    from premiscale.config.v1alpha1 import Config


log = logging.getLogger(__name__)


def start(config: Config, version: str, token: str) -> int:
    """
    Start our subprocesses and the healthcheck API for Docker and Kubernetes.

    Args:
        config (Config): controller config file as a Config object.
        version (str): controller version.
        token (str): controller registration token.

    Returns:
        int: status code of the first subprocess to exit.
    """
    _ret_code = 0

    setproctitle('premiscale')

    # Start the healthcheck and other APIs in a separate thread off our main process as a daemon thread.
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

    for _dthread in _main_process_daemon_threads:
        _dthread.start()

    with ProcessPoolExecutor() as executor, mp.Manager() as manager:

        autoscaling_action_queue: Queue = cast(Queue, manager.Queue())
        platform_message_queue: Queue = cast(Queue, manager.Queue())

        # Submit the core PremiScale subprocesses that don't depend on the controller mode.
        processes = [
            # Platform websocket connection subprocess. Maintains registration, connection and data stream -> premiscale platform).
            executor.submit(
                _platform,
                platform_message_queue
            ) if (_platform := Platform.register(
                version=version,
                token=token,
                host=config.controller.platform.domain,
                cacert=config.controller.platform.certificates.path
            )) is not None else None,

            # Autoscaling controller subprocess (works on Actions in the ASG queue)
            executor.submit(
                Autoscaler(config),
                autoscaling_action_queue
            )
        ]

        # Based on the mode the controller was started in (Kubernetes or standalone), we start the relevant subprocesses.
        match config.controller.mode:
            case 'kubernetes':
                processes.append(
                    executor.submit(
                        MetricsCollector(
                            config,
                            # No need for time-series metrics collection in Kubernetes mode.
                            timeseries_enabled=False
                        )
                    )
                )

                from premiscale.reconciliation.kubernetes import KubernetesAutoscaler

                # Collect actions from the Kubernetes autoscaler and translate them into PremiScale Actions for
                # the Autoscaling subprocess to process.
                processes.append(
                    executor.submit(
                        KubernetesAutoscaler(config),
                        autoscaling_action_queue,
                        platform_message_queue
                    )
                )
            case 'standalone':
                processes.append(
                    executor.submit(
                        MetricsCollector(
                            config,
                            # Enable time-series metrics collection in standalone mode since Reconciliation needs it.
                            timeseries_enabled=True
                        )
                    )
                )

                from premiscale.reconciliation.internal import Reconcile

                # In standalone mode, we reconcile the state of the ASG with the desired state, as determined by analyzing the
                # metrics collected by the MetricsCollector subprocess.
                processes.append(
                    executor.submit(
                        Reconcile(config),
                        autoscaling_action_queue,
                        platform_message_queue
                    )
                )
            case 'standalone-external-metrics':
                from premiscale.reconciliation.internal import Reconcile

                # In standalone mode, we reconcile the state of the ASG with the desired state, as determined by analyzing the
                # metrics collected by the MetricsCollector subprocess.
                processes.append(
                    executor.submit(
                        Reconcile(config),
                        autoscaling_action_queue,
                        platform_message_queue
                    )
                )
            case 'kubernetes-external-metrics':
                from premiscale.reconciliation.kubernetes import KubernetesAutoscaler

                # Collect actions from the Kubernetes autoscaler and translate them into PremiScale Actions for
                # the Autoscaling subprocess to process.
                processes.append(
                    executor.submit(
                        KubernetesAutoscaler(config),
                        autoscaling_action_queue,
                        platform_message_queue
                    )
                )

        filtered_processes = [process for process in processes if process is not None]

        for process in as_completed(filtered_processes):
            try:
                process.result()
            except Exception:
                log.error(f'Process {process} failed. Full traceback: {traceback.format_exc()}')
                _ret_code = 1
                break

    for thread in _main_process_daemon_threads:
        thread.join()

    return _ret_code
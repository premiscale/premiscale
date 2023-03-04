"""
Main agent daemon. There are 3 loops and queues at any given time to

    1) collect host metrics about VMs under management.
"""


import logging
# import asyncio
import signal
import sys

from typing import Any
#from queue import Queue
from threading import Thread
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process, Pool, Queue # this has all the equivalents of threading.Thread
from time import sleep
from contextlib import AbstractContextManager
from daemon import DaemonContext, pidfile
# from websockets import connect
# from config.parse import Config


log = logging.getLogger(__name__)


class PremiScaleDaemon(AbstractContextManager):
    """
    Daemon loops that periodically spawn threads to acquire and publish data from
    hosts to the platform.

    Args:
        interval_metrics (int > 0): interval that the metrics collection daemon thread should
            wake up to spawn threads that acquire data from the list of hosts.
        queue_max_size (int > 0): maximum number of hosts to keep on the shared queue.
    """
    def __init__(self,
            config: dict,
            interval_metrics: int = 10,
            queue_max_size: int = 10,
            queue_timeout: int = 3600
            ) -> None:

        self.config = config
        self.interval_metrics = interval_metrics
        self.queue_max_size = queue_max_size
        self.queue_timeout = queue_timeout

        # Start a non-blocking daemon thread that periodically writes to the queue.
        self.metrics_queue: Queue = Queue(maxsize=queue_max_size)
        self._metrics_daemon = Thread(target=self._d_metrics, daemon=True)
        self._n_metrics_threads = 0

        # Create a client connection, with which we intend to publish measurements.
        # self._ws =

    def publish(self, js: dict) -> None:
        """
        Add a metric to the queue for the daemon to flush periodically. I've kept the
        interface the same as `publish` on `InfluxPublisher`, above.
        Args:
            js: the data to publish (a list of measurements).
        Returns:
            Nothing.
        """
        self.metrics_queue.put(js, timeout=self.queue_timeout)

    # Host metrics collection daemon thread.

    def _d_metrics(self) -> None:
        """
        'Daemonized' collector that has the ability to spin up other threads.
        Periodically wakes up and tries to empty its queue of measurements.
        This method is not meant to be called directly.
        Returns:
            Nothing.
        """
        while True:
            log.debug('Daemon waking up for processing.')
            if not self.metrics_queue.empty():
                # No reason to create more threads than necessary, here.
                if self.queue_max_size > self.metrics_queue.qsize():
                    self._n_metrics_threads = self.metrics_queue.qsize()
                    division = 1
                    remainder = 0
                else:
                    self._n_metrics_threads = self.queue_max_size
                    division = self.metrics_queue.qsize() // self._n_metrics_threads
                    remainder = self.metrics_queue.qsize() % self._n_metrics_threads

                self._spawn_threads_metrics(division, remainder)
            sleep(self.interval_metrics)

    def _spawn_threads_metrics(self, division: int, remainder: int =0) -> None:
        """
        Make publication threads, and return if there's an error during the request.
        Args:
            division: number of thread creation/join cycles to make during drain.
            remainder: number of threads to create in the very last cycle.
        Returns:
            Nothing.
        """
        for _i in [division, remainder]:
            for _ in range(_i):
                q_size_start = self.metrics_queue.qsize()
                threads = []
                for _ in range(self._n_metrics_threads):
                    new_thread = Thread(target=self._t_metrics_collect, args=())
                    log.debug(f'Starting thread {new_thread.getName()}')
                    new_thread.start()
                    threads.append(new_thread)
                for thread in threads:
                    thread.join()
                # If the ending queue size is the same as we started, just wait until
                # the next publish cycle to try again, they're obviously failing.
                if self.metrics_queue.qsize() == q_size_start:
                    return

    def _t_metrics_collect(self) -> None:
        """
        .
        """
        sleep(3)

    # CM

    def start(self) -> None:
        """
        Let the daemons out.
        """
        log.info('Starting PremiScale daemon')
        #self._metrics_daemon.start()
        sleep(100)
        log.info('Successfully started daemon')

    def stop(self, *args: Any) -> None:
        """
        Stop daemons, close db connections gracefully.
        """
        #self._metrics_daemon.join()
        log.info('Stopping PremiScale gracefully')

    def __enter__(self) -> 'PremiScaleDaemon':
        return self

    def __exit__(self, *args: Any) -> None:
        self.stop(*args)


## Each of these classes is its own subprocess of the main daemon process.


class Reconcile(Process):
    """
    Similar to metrics - a reconciliation loop that queries influxdb for the list of VMs
    metrics came from and compares these data to state stored in MySQL. If they don't match,
    actions are added to the queue.
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


class Platform(Process):
    """
    Handle communication to and from the platform. Maintains an async websocket
    connection and calls setters and getters on the other daemon threads' objects to
    configure them.
    """
    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.token = token

    def sync_actions(self) -> bool:
        """
        Sync actions taken by the agent for auditing.

        Returns:
            bool: True if the sync was successful.
        """
        return False

    def sync_metrics(self) -> bool:
        """
        Sync metrics to the platform.

        Returns:
            bool: True if the sync was successful.
        """
        return False


# Use this - https://docs.python.org/3.10/library/concurrent.futures.html?highlight=concurrent#processpoolexecutor
def wrapper(working_dir: str, pid_file: str, agent_config: dict) -> None:
    """
    Wrap our three daemon processes and pass along relevant data.

    Args:
        working_dir (str): working directory for this daemon.
        pid_file (str): PID file to use for the main daemon process.
        agent_config (dict): Agent config object.
    """

    # We need one of these process trees for every ASG.

    autoscaling_action_queue: Queue = Queue()
    platform_message_queue: Queue = Queue()

    with PremiScaleDaemon(agent_config) as premiscale_d, DaemonContext(
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            detach_process=False,
            prevent_core=True,
            pidfile=pidfile.TimeoutPIDLockFile(pid_file),
            working_directory=working_dir,
            signal_map={
                signal.SIGTERM: premiscale_d.stop,
                signal.SIGHUP: premiscale_d.stop,
                signal.SIGINT: premiscale_d.stop,
            }
        ):
        premiscale_d.start()
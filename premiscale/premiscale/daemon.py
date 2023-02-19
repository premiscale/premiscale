"""
Main agent daemon. There are 3 loops and queues at any given time to

    1) collect host metrics about VMs under management.
"""


import logging
# import asyncio
import signal

from typing import Any
from queue import Queue
from threading import Thread
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
                interval_metrics: int = 10,
                queue_max_size: int = 10,
                queue_timeout: int = 3600
                ) -> None:

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
        log.info('Starting PremiScale daemon.')
        self._metrics_daemon.start()
        log.info('Successfully started daemon.')

    def stop(self, *args: Any) -> None:
        """
        Stop daemons, close db connections gracefully.
        """
        self._metrics_daemon.join()
        log.info('Stopping PremiScale gracefully.')

    def __enter__(self) -> 'PremiScaleDaemon':
        return self

    def __exit__(self, *args: Any) -> None:
        self.stop(*args)


def premiscale_daemon(pid_file: str, working_dir: str) -> None:
    with PremiScaleDaemon() as d, \
         DaemonContext(pidfile=pidfile.TimeoutPIDLockFile(pid_file), working_directory=working_dir) as _d:

        log.debug('Started daemon context.')

        _d.signal_map = {
            signal.SIGTERM: d.stop,
            signal.SIGHUP: d.stop,
        }

        d.start()
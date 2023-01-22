"""
Daemon loop.
"""


import logging
import asyncio

from typing import Any
from queue import Queue
from threading import Thread
from time import sleep
from websockets import connect


log = logging.getLogger(__name__)


class PremiScaleDaemon:
    """
    Daemon loops that periodically spawn threads to acquire and publish data from hosts to the platform.

    Args:
        interval_publish (int > 0): interval that the publication daemon thread wakes to publish host data on-queue.
        interval_evaluation (int > 0): interval that metrics from hosts should be evaluated, logic behind autoscaling decisions.
        interval_metrics (int > 0): interval that the metrics collection daemon thread should wake up to spawn threads that acquire data from the list of hosts.
        queue_max_size (int > 0): maximum number of hosts to keep on the shared queue.
    """
    def __init__(self,
                mysql_username: str,
                mysql_password: str,
                mysql_connection_string: str,
                influx_username: str,
                influx_password: str,
                influx_connection_string: str,
                interval_publish: int = 10,
                interval_metrics: int = 10,
                queue_max_size: int = 10,
                queue_timeout: int = 3600
                ) -> None:
        self.interval_publish = interval_publish
        self.interval_metrics = interval_metrics

        self.queue_max_size = queue_max_size
        self.queue_timeout = queue_timeout

        self.platform_queue: Queue = Queue(maxsize=queue_max_size)
        self.metrics_queue: Queue = Queue(maxsize=queue_max_size)
        self._n_threads = 0

        # Start a non-blocking daemon thread that periodically reads from the queue.
        self._platform_daemon = Thread(target=self._d_platform, daemon=True)
        self._platform_daemon.start()

        # Start a non-blocking daemon thread that periodically writes to the queue.
        self._metrics_daemon = Thread(target=self._d_metrics, daemon=True)
        self._metrics_daemon.start()

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

    # Local metrics

    def _d_metrics(self) -> None:
        """
        'Daemonized' publisher that has the ability to spin up other threads.
        Periodically wakes up and tries to empty its queue of measurements.
        This method is not meant to be called directly.
        Returns:
            Nothing.
        """
        while True:
            if not self.metrics_queue.empty():
                # No reason to create more threads than necessary, here.
                if self.queue_max_size > self.metrics_queue.qsize():
                    self._n_threads = self.metrics_queue.qsize()
                    division = 1
                    remainder = 0
                else:
                    self._n_threads = self.queue_max_size
                    division = self.metrics_queue.qsize() // self._n_threads
                    remainder = self.metrics_queue.qsize() % self._n_threads

                self._spawn_threads_metrics(division, remainder)
            sleep(self.interval_publish)

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
                for _ in range(self._n_threads):
                    new_thread = Thread(target=self._t_publish, args=())
                    new_thread.start()
                    threads.append(new_thread)
                for thread in threads:
                    thread.join()
                # If the ending queue size is the same as we started, just wait until
                # the next publish cycle to try again, they're obviously failing.
                if self.metrics_queue.qsize() == q_size_start:
                    return None

    # Platform metrics.

    def _d_platform(self) -> None:
        """
        'Daemonized' publisher that has the ability to spin up other threads.
        Periodically wakes up and tries to empty its queue of measurements.
        This method is not meant to be called directly.
        Returns:
            Nothing.
        """
        while True:
            if not self.platform_queue.empty():
                # No reason to create more threads than necessary, here.
                if self.queue_max_size > self.platform_queue.qsize():
                    self._n_threads = self.platform_queue.qsize()
                    division = 1
                    remainder = 0
                else:
                    self._n_threads = self.queue_max_size
                    division = self.platform_queue.qsize() // self._n_threads
                    remainder = self.platform_queue.qsize() % self._n_threads

                self._spawn_threads_platform(division, remainder)
            sleep(self.interval_metrics)

    def _spawn_threads_platform(self, division: int, remainder: int =0) -> None:
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
                q_size_start = self.platform_queue.qsize()
                threads = []
                for _ in range(self._n_threads):
                    new_thread = Thread(target=self._t_publish, args=())
                    new_thread.start()
                    threads.append(new_thread)
                for thread in threads:
                    thread.join()
                # If the ending queue size is the same as we started, just wait until
                # the next publish cycle to try again, they're obviously failing.
                if self.platform_queue.qsize() == q_size_start:
                    return None

    def _t_publish(self) -> None:
        """
        Publish a datum point to the platform.
        """

    def __enter__(self) -> 'PremiScaleDaemon':
        return self

    def __exit__(self, *args: Any) -> None:
        # TODO: figure out the correct way to kill the daemon safely?
        pass


def start_daemon() -> None:
    """
    Blocking function that spawns PremiScale's daemons (one for gathering host data, and another for
    publishing and evaluating host data).
    """

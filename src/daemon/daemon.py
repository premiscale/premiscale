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
        queue_timeout (int > 0): maximum amount of time host data should reside on the queue.
    """
    def __init__(self, interval_publish: int = 10, interval_metrics: int = 10, queue_max_size: int = 10, queue_timeout: int = 3600) -> None:
        self.interval_publish = interval_publish
        self.interval_metrics = interval_metrics

        self.queue_max_size = queue_max_size
        self.queue_timeout = queue_timeout

        self.queue: Queue = Queue(maxsize=queue_max_size)
        self._n_threads = 0

        # Start a non-blocking daemon thread that periodically reads from the queue.
        self._publish_daemon = Thread(target=self._d_publish, daemon=True)
        self._publish_daemon.start()

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
        self.queue.put(js, timeout=self.queue_timeout)

    def _d_publish(self) -> None:
        """
        'Daemonized' publisher that has the ability to spin up other threads.
        Periodically wakes up and tries to empty its queue of measurements.
        This method is not meant to be called directly.
        Returns:
            Nothing.
        """
        while True:
            if not self.queue.empty():
                # No reason to create more threads than necessary, here.
                if self.queue_max_size > self.queue.qsize():
                    self._n_threads = self.queue.qsize()
                    division = 1
                    remainder = 0
                else:
                    self._n_threads = self.queue_max_size
                    division = self.queue.qsize() // self._n_threads
                    remainder = self.queue.qsize() % self._n_threads

                self._spawn_threads(division, remainder)
            sleep(self.interval_publish)

    def _d_metrics(self) -> None:
        """
        'Daemonized' publisher that has the ability to spin up other threads.
        Periodically wakes up and tries to empty its queue of measurements.
        This method is not meant to be called directly.
        Returns:
            Nothing.
        """
        while True:
            if not self.queue.empty():
                # No reason to create more threads than necessary, here.
                if self.queue_max_size > self.queue.qsize():
                    self._n_threads = self.queue.qsize()
                    division = 1
                    remainder = 0
                else:
                    self._n_threads = self.queue_max_size
                    division = self.queue.qsize() // self._n_threads
                    remainder = self.queue.qsize() % self._n_threads

                self._spawn_threads(division, remainder)
            sleep(self.interval_metrics)

    def _spawn_threads(self, division: int, remainder: int =0) -> None:
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
                q_size_start = self.queue.qsize()
                threads = []
                for _ in range(self._n_threads):
                    new_thread = Thread(target=self.t_publish, args=())
                    new_thread.start()
                    threads.append(new_thread)
                for thread in threads:
                    thread.join()
                # If the ending queue size is the same as we started, just wait until
                # the next publish cycle to try again, they're obviously failing.
                if self.queue.qsize() == q_size_start:
                    return None

    def t_publish(self) -> None:
        """
        Publish a datum point to the client.
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

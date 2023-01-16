"""
Daemon loop.
"""


import logging
from queue import LifoQueue, Queue
from threading import Thread

from config.parse import env


log = logging.getLogger(__name__)


class DaemonInfluxPublisher:
    """
    Provide an interface to a daemon that periodically flushes a queue of data points.
    """
    def __init__(self, credentials: str) -> None:
        self.queue: Queue = LifoQueue(maxsize=env['QUEUE_MAX'])
        self._n_threads = 0

        # Start a non-blocking daemon thread that's created and periodically reads
        # from the queue, as well as spins up additional threads.
        # self._publish_daemon = Thread(target=self._d_publisher, daemon=True)
        # self._publish_daemon.start()

        # Create a client connection, with which we intend to publish measurements.
        # self._client = InfluxDBClient(**read_credentials(credentials))

    # def publish(self, js: measureT) -> None:
    #     """
    #     Add a metric to the queue for the daemon to flush periodically. I've kept the
    #     interface the same as `publish` on `InfluxPublisher`, above.
    #     Args:
    #         js: the data to publish (a list of measurements).
    #     Returns:
    #         Nothing.
    #     """
    #     self.queue.put(js, timeout=env['QUEUE_TIMEOUT'])

    # def _d_publisher(self) -> None:
    #     """
    #     'Daemonized' publisher that has the ability to spin up other threads.
    #     Periodically wakes up and tries to empty its queue of measurements.
    #     This method is not meant to be called directly.
    #     Returns:
    #         Nothing.
    #     """
    #     while True:
    #         if not self.queue.empty():
    #             # No reason to create more threads than necessary, here.
    #             if env['MAX_THREADS'] > self.queue.qsize():
    #                 self._n_threads = self.queue.qsize()
    #                 division = 1
    #                 remainder = 0
    #             else:
    #                 self._n_threads = env['MAX_THREADS']
    #                 division = self.queue.qsize() // self._n_threads
    #                 remainder = self.queue.qsize() % self._n_threads

    #             self._spawn_threads(division, remainder)
    #         sleep(env['DAEMON_WAKEUP'])

    # def _spawn_threads(self, division: int, remainder: int =0) -> None:
    #     """
    #     Make publication threads, and return if there's an error during the request.
    #     Args:
    #         division: number of thread creation/join cycles to make during drain.
    #         remainder: number of threads to create in the very last cycle.
    #     Returns:
    #         Nothing.
    #     """
    #     for _i in [division, remainder]:
    #         for _ in range(_i):
    #             q_size_start = self.queue.qsize()
    #             threads = []
    #             for _ in range(self._n_threads):
    #                 new_thread = Thread(target=self.t_publish, args=())
    #                 new_thread.start()
    #                 threads.append(new_thread)
    #             for thread in threads:
    #                 thread.join()
    #             # If the ending queue size is the same as we started, just wait until
    #             # the next publish cycle to try again, they're obviously failing.
    #             if self.queue.qsize() == q_size_start:
    #                 return None

    # def t_publish(self) -> None:
    #     """
    #     Publish a list of measurements to the open client connection on an influxdb.
    #     Args:
    #         p: the measures to publish.
    #     Returns:
    #         Nothing.
    #     """
    #     p: measureT = self.queue.get()
    #     try:
    #         self._client.write_points(p)
    #     except ConnectionError:
    #         # Just put the item back on the queue lol.
    #         self.queue.put(p)

    # def __enter__(self) -> 'DaemonInfluxPublisher':
    #     return self

    # def __exit__(self, *args: Any) -> None:
    #     # TODO: figure out the correct way to kill the daemon safely?
    #     pass
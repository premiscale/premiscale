"""
Methods relating to connecting to PremiScale's platform.
"""

import asyncio
import logging
import time
import websockets as ws
import socket

from typing import Dict
from multiprocessing.queues import Queue
from urllib.parse import urljoin


log = logging.getLogger(__name__)


def register(token: str, endpoint: str = 'https://app.premiscale.com', path: str = '/agent/registration') -> bool:
    """
    Make a request to the registration service.

    Args:
        token (str): registration API token.
        endpoint (str): platform domain.
        path (str): endpoint to hit at the platform domain.

    Returns:
        bool: True if the registration was successful, False otherwise.
    """
    url = urljoin(endpoint, path)

    return True


class Platform:
    """
    Handle communication to and from the platform. Maintains an async websocket
    connection and calls setters and getters on the other daemon threads' objects to
    configure them.
    """
    def __init__(self, url: str, token: str, path: str = '/agent/websocket') -> None:
        # Path needs to align with the Helm chart's ingress.
        self.url = urljoin('wss://' + url, path)
        self._token = token
        self.websocket = None
        self.queue: Queue
        self._auth: Dict

    def __call__(self, platform_queue: Queue) -> None:
        self.queue = platform_queue
        log.debug('Starting platform connection subprocess')
        # This should never exit. Process should stay open forever.
        asyncio.run(self._set_up_connection())

    async def sync_actions(self) -> bool:
        """
        Sync actions taken by the agent for auditing.

        Returns:
            bool: True if the sync was successful.
        """
        return False

    async def sync_metrics(self) -> bool:
        """
        Sync metrics to the platform.

        Returns:
            bool: True if the sync was successful.
        """
        return False

    async def send_message(self, msg: str) -> None:
        """
        Send an arbitrary message to the platform.

        Args:
            msg (str): Message to send.

        Returns:
            bool: True if the send was successful.
        """
        if not self.websocket:
            log.error('Cannot submit arbitrary message to platform, connection has not been established.')
        else:
            await self.websocket.send(msg)

    async def _sync_platform_queue(self) -> None:
        """
        Sync the platform queue with the platform. If this function returns, then the queue is empty.
        """
        # Clear the queue.
        while (msg := self.queue.get()) is not None:
            await self.send_message(msg)
        else:
            await self.send_message('')

    async def _set_up_connection(self) -> None:
        """
        Establish websocket connection to PremiScale's platform.
        """
        while True:
            try:
                async with ws.connect(self.url, ping_timeout=300) as self.websocket:
                    try:
                        log.info(f'Established connection to platform hosted at \'{self.url}\'')
                        while True:
                            await self._sync_platform_queue()
                            time.sleep(5)
                        # await asyncio.Future()
                    except ws.ConnectionClosed:
                        log.error(f'Websocket connection to \'{self.url}\' closed unexpectedly, reconnecting...')
                        continue
            except socket.gaierror as msg:
                log.error(f'Could not connect to \'{self.url}\', retrying: {msg}')
                time.sleep(1)
                continue
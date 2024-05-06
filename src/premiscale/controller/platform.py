"""
Methods relating to connecting to PremiScale's platform.
"""

import asyncio
import logging
import time
import ssl
import requests
import json
import ssl

from typing import Dict, Callable, Optional, Any

from websockets import client as ws, exceptions as wse
from socket import gaierror
from functools import wraps
from multiprocessing.queues import Queue
from urllib.parse import urljoin
from urllib.error import URLError
from http import HTTPStatus
from setproctitle import setproctitle


log = logging.getLogger(__name__)


class RateLimitedError(Exception):
    """
    Raised when an HTTPStatus.TOO_MANY_REQUESTS code is received.
    """
    def __init__(self, message: str ='', delay: float =30.0) -> None:
        super().__init__(message)
        self.message = message
        self.delay = delay

    def __str__(self):
        return f'RateLimitedError(message="{self.message}", code="{HTTPStatus.TOO_MANY_REQUESTS}", "x-rate-limit-reset={self.delay}")'


def retry(tries: int =0) -> Callable:
    """
    A request retry decorator. If singledispatch becomes compatible with `typing`, it'd be cool to duplicate this
    registering another dispatch on `f`, allowing us to remove a layer of function calls.

    Args:
        tries: number of times to retry the wrapped function call. When `0`, retries indefinitely.

    Returns:
        Either the result of a successful function call (be it via retrying or not).
    """
    if tries < 0:
        raise ValueError(f'Expected positive `tries` values, received: "{tries}"')

    def _f(f: Callable) -> Callable:
        @wraps(f)
        def new_f(*args: Any, **kwargs: Any) -> Optional[Dict]:
            res: Any = None

            def call() -> bool:
                nonlocal res

                try:
                    return f(*args, **kwargs)
                except RateLimitedError as msg:
                    log.warning(f'Ratelimited, waiting "{msg.delay}" before trying again')
                    time.sleep(msg.delay)
                    return False
                except URLError as msg:
                    log.warning(msg)
                    return False

            if tries > 0:
                for _ in range(tries):
                    if call():
                        return res
                else:
                    log.error(f'Could not register agent, retry attempt limit exceeded.')
                    return None
            else:
                while not call():
                    pass
                else:
                    return res

        return new_f
    return _f


@retry()
def register(token: str, version: str, domain: str, path: str = '/agent/registration', cacert: str = '') -> bool:
    """
    Make a request to the registration service.

    Args:
        token (str): registration API token.
        version (str): agent version.
        domain (str): platform domain.
        path (str): endpoint to hit at the platform domain.
        cacert (str): path to the CA certificate file.

    Returns:
        bool: True if the registration was successful, False otherwise.

    Raises:
        RateLimitedError: if the request is rate limited.
    """
    url = urljoin(domain, path)

    payload = {
        'version': version,
        'type': 'agent',
        'registration_key': token
    }

    try:
        response = requests.post(
            url=url,
            data=json.dumps(payload),
            headers={
                # 'Authorization': header,
                'Content-Type': 'application/json'
            },
            verify=cacert
        )
    except (ssl.SSLCertVerificationError, requests.exceptions.SSLError) as msg:
        log.error(f'Could not verify SSL certificate: {msg}')
        return False

    try:
        return response.json()
    except json.JSONDecodeError:
        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise RateLimitedError(delay=float(response.headers['x-rate-limit-reset']) / 1_000 + 0.25)
        else:
            log.error(
                f'Did not get valid JSON in response: {response.text if response.text else response.reason} ~ {response.status_code}'
            )
            return False


class Platform:
    """
    Handle communication to and from the platform. Maintains an async websocket
    connection and calls setters and getters on the other daemon threads' objects to
    configure them.
    """
    def __init__(self, url: str, registration: dict, path: str = '/agent/websocket', cacert: str = '') -> None:
        # Path needs to align with the Helm chart's ingress.
        self.url = urljoin('wss://' + url, path)
        self._registration = registration
        print(self._registration)
        self._websocket: ws.WebSocketClientProtocol
        self._cacert = cacert
        self.queue: Queue
        self._auth: Dict

    def __call__(self, platform_queue: Queue) -> None:
        setproctitle('platform')
        self.queue = platform_queue
        log.debug('Starting platform connection subprocess')
        # This should never exit. Process should stay open forever.
        asyncio.run(
            self._set_up_connection()
        )

    async def _set_up_connection(self) -> None:
        """
        Establish websocket connection to PremiScale's platform.
        """
        ssl_context: ssl.SSLContext | None = None

        # Handle self-signed certificates if provided. Build a custom SSL context.
        if self._cacert != '':
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.load_verify_locations(
                cafile=self._cacert
            )

        while True:
            try:
                async with ws.connect(self.url, ping_timeout=300, ssl=ssl_context) as self._websocket:
                    log.info(f'Established connection to platform hosted at \'{self.url}\'')

                    try:
                        await self._sync_platform_queue()
                        await self._recv_message()
                        # await asyncio.Future()
                    except wse.ConnectionClosed:
                        log.error(f'Websocket connection to \'{self.url}\' closed unexpectedly, reconnecting...')
                        continue
            except (gaierror, ssl.SSLError) as msg:
                log.error(f'Could not connect to \'{self.url}\', retrying: {msg}')
                time.sleep(1)
                continue

    async def _sync_platform_queue(self) -> None:
        """
        Sync the platform queue with the platform. If this function returns, then the queue is empty.
        """
        # Clear the queue.
        while (msg := self.queue.get()) is not None:
            await self.send_message(msg)
        else:
            await self.send_message('')

    async def _recv_message(self) -> None:
        """
        Receive messages from the platform.
        """
        async for msg in self._websocket:
            self.queue.put(msg)

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
        Asynchronously send a message up to the platform.

        Args:
            msg (str): Message to send.

        Returns:
            bool: True if the send was successful.
        """
        if not self._websocket:
            log.error('Cannot submit message to platform, connection has not been established.')
        else:
            self.queue.put(msg)
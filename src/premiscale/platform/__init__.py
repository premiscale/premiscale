"""
Methods relating to connecting to PremiScale's platform.
"""


from __future__ import annotations

import asyncio
import logging
import time
import ssl
import requests
import json
import ssl

from typing import Dict
from websockets import client as ws, exceptions as wse
from socket import gaierror
from multiprocessing.queues import Queue
from urllib.parse import urljoin
from http import HTTPStatus
from setproctitle import setproctitle
from premiscale.exceptions import RateLimitedError
from premiscale.utils import write_json, read_json
from premiscale.platform.utils import retry


log = logging.getLogger(__name__)


class Platform:
    """
    Handle communication to and from the platform. Maintains an async websocket
    connection and calls setters and getters on the other daemon threads' objects to
    configure them.

    Args:
        registration (Dict[str, str]): registration response from the registration service.
        version (str): controller version.
        host (str): platform host.
        wspath (str): path to the websocket endpoint.
        cacert (str): path to the certificate file (for use with self-signed certificates).
    """
    def __init__(self,
            registration: Dict[str, str],
            version: str,
            host: str = 'app.premiscale.com',
            wspath: str = '/agent/websocket',
            cacert: str = ''
        ) -> None:

        self.host = urljoin(
            f'wss://{host}',
            wspath
        )

        self.version = version
        self._registration = registration
        self._cacert = cacert

        self._queue: Queue
        self._received_platform_messages: asyncio.Queue = asyncio.Queue()
        self._websocket: ws.WebSocketClientProtocol

    @classmethod
    @retry(retries=3, retry_delay=5.0)
    def register(
            cls,
            token: str,
            version: str,
            host: str,
            registration_path: str = '/agent/registration',
            websocket_path: str = '/agent/websocket',
            cacert: str = ''
        ) -> Platform | None:
        """
        Register the controller with the PremiScale platform before starting this process. If registration fails, this
        classmethod returns None to the upstream caller.

        Args:
            token (str): registration API token.
            version (str): agent version.
            host (str): platform domain.
            registration_path (str): path to the registration endpoint.
            websocket_path (str): path to the controller websocket endpoint.
            cacert (str): path to the CA certificate file, if provided.

        Returns:
            Platform | None: registration service response, or an empty dict if the registration was not successful.

        Raises:
            RateLimitedError: if the request is rate limited.
        """

        # If the controller has already registered, skip the registration request.
        if (cached_registration_response := read_json('registration.json')) is not None and cached_registration_response.get('host') == host:
            log.info(f'Agent already registered with PremiScale platform at "{host}". Skipping controller registration request')
        else:
            # If no token is provided and a cached registration response is not found, simply start the controller
            # in standalone mode for development purposes.
            if token == '':
                log.warning('No registration token provided, starting controller in standalone mode')
                return None

            try:
                response = requests.post(
                    url=urljoin(
                        f'https://{host}',
                        registration_path
                    ),

                    data=json.dumps(
                        {
                            'version': version,
                            'type': 'agent',
                            'registration_key': token
                        }
                    ),
                    headers={
                        # 'Authorization': header,
                        'Content-Type': 'application/json'
                    },
                    verify=cacert
                )

                if response.status_code != HTTPStatus.OK:
                    log.error(f'Failed to register with PremiScale platform: {response.text}')
                    return None

                registration_response = response.json()

                log.debug(f'Registration response: {json.dumps(registration_response)}')

                # Append the host used to make the registration request to the registration response.
                registration_response['host'] = host

                # Write the registration response to disk for future reference; if the controller is restarted, it will
                # Attempt to read this file to determine if it has already registered. If the host changes, the controller
                # will re-register and be assigned a new agent ID by the platform.
                write_json(registration_response, '$HOME/registration.json')

            except (ssl.SSLCertVerificationError, requests.exceptions.SSLError) as msg:
                log.error(f'Could not verify SSL certificate: {msg}. Skipping registration')

                return None
            except json.JSONDecodeError:
                if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    # Kick a RateLimitedError exception to the retry decorator to attempt the request again.
                    raise RateLimitedError(delay=float(response.headers['x-rate-limit-reset']) / 1_000)
                else:
                    log.error(
                        f'Did not get valid JSON in response: {response.text if response.text else response.reason} ~ {response.status_code}'
                    )

                    return None

        return cls(
            registration=registration_response,
            version=version,
            host=host,
            wspath=websocket_path,
            cacert=cacert
        )

    def __call__(self, platform_queue: Queue) -> None:
        setproctitle('platform')
        self._queue = platform_queue
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
                async with ws.connect(self.host, ping_timeout=300, ssl=ssl_context) as self._websocket:
                    log.info(f'Established connection to platform hosted at \'{self.host}\'')

                    try:
                        await asyncio.gather(
                            self._recv_message(),
                            self._sync_platform_queue()
                        )
                    except wse.ConnectionClosed:
                        log.error(f'Websocket connection to \'{self.host}\' closed unexpectedly, reconnecting...')
            except (gaierror, ssl.SSLError) as msg:
                log.error(f'Could not connect to \'{self.host}\', retrying: {msg}')
                time.sleep(2)

    async def _sync_platform_queue(self) -> None:
        """
        Sync the platform queue with the platform. If this function returns, then the queue is empty.
        """
        while True:
            if not self._queue.empty():
                for _ in range(self._queue.qsize()):
                    msg = self._queue.get()
                    await self.send_message(msg)
            await asyncio.sleep(1)

    async def _recv_message(self) -> None:
        """
        Receive messages from the platform and place them on a separate queue to be acted upon.
        """
        async for msg in self._websocket:
            await self._received_platform_messages.put(msg)

    async def sync_actions(self) -> bool:
        """
        Sync actions taken by the controller for auditing.

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

    async def send_message(self, msg: str) -> bool:
        """
        Asynchronously send a message up to the platform.

        Args:
            msg (str): Message to send.

        Returns:
            bool: True if the item was queued.
        """
        self._queue.put(msg)
        return True
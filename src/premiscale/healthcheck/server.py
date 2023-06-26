"""
Serve premiscale agent healthcheck endpoint when in daemon mode. Follows the same pattern as the agent and registration service.
"""

import logging
import gunicorn.app.base as base

from typing import Dict, Optional, Any
from setproctitle import setproctitle
from http import HTTPStatus
from flask import Flask, Response
from flask_cors import CORS


api = Flask(__name__)
CORS(api)

log = logging.getLogger(__name__)


@api.get('/agent/websocket/healthcheck')
def healthcheck() -> Response:
    """
    Quick healthcheck endpoint.

    Returns:
        dict: an object with schema like

        {
            "status": "OK"
        }
    """
    return Response(
        {
            'status': 'OK'
        },
        status=HTTPStatus.OK,
        mimetype='application/json'
    )


class Healthcheck(base.Application):
    """
    Custom gunicorn application so we can start this service via the echoes service CLI.
    """
    def __init__(self, options: Optional[Dict] = None, app: Optional[Flask] = None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def __call__(self) -> int:
        """
        Start the flask app.

        Returns:
            (int): an exit code of 1. This subprocess should never stop running. If it does, there's a bug/reason.
        """
        setproctitle('healthcheck')
        log.debug('started healthcheck server')

        self.run()

        return 1

    def __enter__(self) -> 'Healthcheck':
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    def load_config(self):
        """
        Load a gunicorn config map instead of the traditional config file.
        """
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
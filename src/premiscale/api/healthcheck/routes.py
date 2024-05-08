"""
Serve premiscale agent healthcheck endpoint when in daemon mode.
"""

import logging

from http import HTTPStatus
from flask import Flask, Response
from flask_cors import CORS


api = Flask(__name__)
CORS(api)

log = logging.getLogger(__name__)


def healthcheck() -> Flask:
    """
    Create a healthcheck API server.
    """
    app = Flask(__name__)
    CORS(app)

    @app.get('/healthcheck')
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

    return app



class Healthcheck:
    """
    Healthcheck API server.
    """
    def __init__(self, host: str = 'localhost', port: int = 8085) -> None:
        self.host = host
        self.port = port
        self.server = None
        # self.server = WSGIServer(
        #     (
        #         host,
        #         port
        #     ),
        #     api
        # )

    def __call__(self) -> None:
        self.run()

    def run(self) -> None:
        """
        Start the healthcheck API server.
        """
        # self.server.serve_forever()
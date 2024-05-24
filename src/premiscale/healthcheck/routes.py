"""
Serve PremiScale controller healthcheck endpoint when in daemon mode.
"""


from http import HTTPStatus
from flask import Response
from flask import Flask

import logging


log = logging.getLogger(__name__)


def create_healthcheck_api(app: Flask) -> None:
    """
    Create a healthcheck API for a Flask app instance.

    Args:
        app (Flask): Flask app instance.
    """

    @app.get('/healthcheck')
    def healthcheck() -> Response:
        """
        Quick unauthenticated healthcheck endpoint.

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
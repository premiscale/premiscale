"""
Serve a /metrics-endpoint for Prometheus metrics if enabled.
"""


from __future__ import annotations

from typing import TYPE_CHECKING
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app


if TYPE_CHECKING:
    from flask import Flask


def create_metrics_api(app: Flask) -> None:
    """
    Create a metrics API endpoint monitoring the health of the controller.

    Args:
        app (Flask): Flask app instance.
    """

    # app.wsgi_app = DispatcherMiddleware(
    #     app.wsgi_app,
    #     {
    #         '/metrics': make_wsgi_app()
    #     }
    # )
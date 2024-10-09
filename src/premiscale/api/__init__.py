"""
Merge all the API endpoints into a single blueprint.
"""


import logging


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# from flask import Blueprint
# from flask_cors import CORS


# api = Blueprint('api', __name__)
# CORS(api)


# from premiscale.api.healthcheck.routes import create_healthcheck_api
# from premiscale.api.metrics.routes import create_metrics_api


# create_healthcheck_api(api)
# create_metrics_api(api)


# __all__ = ['api']
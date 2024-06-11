"""
This module is responsible for the metrics API. Scrape metrics from the Prometheus server and return them to the user.
"""


from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


__all__ = ['app']


from premiscale.api.metrics.routes import create_metrics_api


create_metrics_api(app)
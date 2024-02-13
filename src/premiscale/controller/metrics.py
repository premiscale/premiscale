import logging

from setproctitle import setproctitle


log = logging.getLogger(__name__)


class Metrics:
    """
    Handle metrics collection from hosts. Only one of these loops is created; metrics
    are published to influxdb for retrieval and query by the ASG loop, which evaluates
    on a per-ASG basis whether Actions need to be taken.
    """
    def __init__(self, connection: dict) -> None:
        match connection['type']:
            case 'influxdb':
                from src.premiscale.metrics.influxdb import InfluxDB
                del(connection['type'])
                self.metrics_database = InfluxDB(**connection)

    def __call__(self) -> None:
        setproctitle('metrics')
        log.debug('Starting metrics collection subprocess')
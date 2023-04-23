"""
Parse config files with the v1alpha1 config-parsing class.
"""


from typing import Optional, Any, Dict
from premiscale.config._config import Config

import logging
import os
import sys


log = logging.getLogger(__name__)


class Config_v1alpha1(Config):
    """
    Class that encapsulates access methods and parsing config version v1alpha1.
    """

    # Top-level.

    def agent(self) -> Dict:
        """
        Get the agent config dict.

        Returns:
            Dict: the agent config dict.
        """
        return self.config['agent']

    def autoscale(self) -> Dict:
        """
        Get the autoscale config dict.

        Returns:
            Dict: _description_
        """
        return self.config['autoscaling']

    ## Secondary-level.

    def daemon(self) -> Dict:
        """
        Get the daemon configuration options as a flat map.

        Returns:
            Dict: The daemon configuration options.
        """
        return self.agent()['daemon']

    def databases(self) -> Dict:
        """
        Get the autoscaling databases configuration map.

        Returns:
            Dict: The autoscale.databases config map.
        """
        return self.agent()['databases']

    def hosts(self) -> Dict:
        """
        Get the host groups list from the autoscaling map.

        Returns:
            Dict: The host groups list.
        """
        return self.autoscale()['hosts']

    def groups(self) -> Dict:
        """
        Get the autoscaling groups list from the autoscaling map.

        Returns:
            Dict: The autoscaling groups list.
        """
        return self.autoscale()['groups']

    ### Databases.

    def state_database_connection(self) -> Dict:
        """
        Get the state database credentials (MySQL).

        Returns:
            Dict: MySQL configuration and credentials.
        """
        match (state := self.databases()['state'])['type']:
            case 'mysql':
                mysql_connect = state['connection']
                return {
                    'url': mysql_connect['url'],
                    'database': mysql_connect['database'],
                    'username': os.getenv(mysql_connect['credentials']['username']),
                    'password': os.getenv(mysql_connect['credentials']['password']),
                    'reconcile_interval': state['reconcileInterval']
                }
            case _:
                log.error(f'State database type \'{self.databases()["state"]["type"]}\' unsupported')
                sys.exit(1)

    def metrics_database_connection(self) -> Dict:
        """
        Get the metrics database credentials (InfluxDB).

        Returns:
            Dict: InfluxDB configuration and credentials.
        """
        match (metrics := self.databases()['metrics'])['type']:
            case 'influxdb':
                influxdb_connect = metrics['connection']
                return {
                    'url': influxdb_connect['url'],
                    'database': influxdb_connect['database'],
                    'username': os.getenv(influxdb_connect['credentials']['username']),
                    'password': os.getenv(influxdb_connect['credentials']['password']),
                    'collection_interval': metrics['collectionInterval'],
                    'max_threads': metrics['maxThreads'],
                    'host_connection_timeout': metrics['hostConnectionTimeout'],
                    'trailing': metrics['trailing']
                }
            case _:
                log.error(f'Metrics database type \'{self.databases()["metrics"]["type"]}\' unsupported')
                sys.exit(1)

    # def metrics_database_configuration(self) -> Dict:
    #     """
    #     Get the metrics

    #     Returns:
    #         Dict: _description_
    #     """
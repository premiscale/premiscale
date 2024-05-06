"""
Parse config files with the v1alpha1 config-parsing class.
"""


from typing import Dict
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

    def agent_daemon(self) -> Dict:
        """
        Get the daemon configuration options as a flat map.

        Returns:
            Dict: The daemon configuration options.
        """
        return self.agent()['daemon']

    def agent_databases(self) -> Dict:
        """
        Get the autoscaling databases configuration map.

        Returns:
            Dict: The autoscale.databases config map.
        """
        return self.agent()['databases']

    def autoscale_hosts(self) -> Dict:
        """
        Get the host groups list from the autoscaling map.

        Returns:
            Dict: The host groups list.
        """
        return self.autoscale()['hosts']

    def autoscale_groups(self) -> Dict:
        """
        Get the autoscaling groups list from the autoscaling map.

        Returns:
            Dict: The autoscaling groups list.
        """
        return self.autoscale()['groups']

    ### Databases

    #### state

    def agent_databases_state_connection(self) -> Dict:
        """
        Get the state database credentials (MySQL).

        Returns:
            Dict: MySQL configuration and credentials.
        """
        match (state := self.agent_databases()['state'])['type']:
            case 'mysql':
                mysql_connect = state['connection']
                return {
                    'type': 'mysql',
                    'url': os.path.expandvars(mysql_connect['url']),
                    'database': os.path.expandvars(mysql_connect['database']),
                    'username': os.path.expandvars(mysql_connect['credentials']['username']),
                    'password': os.path.expandvars(mysql_connect['credentials']['password'])
                }
            case _:
                log.error(f'State database type \'{state["type"]}\' unsupported')
                sys.exit(1)

    def agent_databases_state_configuration(self) -> Dict:
        """
        Get the state database credentials (MySQL).

        Returns:
            Dict: MySQL configuration and credentials.
        """
        match (state := self.agent_databases()['state'])['type']:
            case 'mysql':
                return {
                    'type': 'mysql',
                    'reconcile_interval': state['reconcileInterval']
                }
            case _:
                log.error(f'State database type \'{state["type"]}\' unsupported')
                sys.exit(1)

    #### metrics

    def agent_databases_metrics_connection(self) -> Dict:
        """
        Get the metrics database credentials (InfluxDB).

        Returns:
            Dict: Metrics database credentials.
        """
        match (metrics := self.agent_databases()['metrics'])['type']:
            case 'influxdb':
                influxdb_connect = metrics['connection']
                return {
                    'type': 'influxdb',
                    'url': os.path.expandvars(influxdb_connect['url']),
                    'database': os.path.expandvars(influxdb_connect['database']),
                    'username': os.path.expandvars(influxdb_connect['credentials']['username']),
                    'password': os.path.expandvars(influxdb_connect['credentials']['password'])
                }
            case _:
                log.error(f'Metrics database type \'{metrics["type"]}\' unsupported')
                sys.exit(1)

    def agent_databases_metrics_configuration(self) -> Dict:
        """
        Get the metrics database configuration (whereas the last method retrieved the credentials/auth data).

        Returns:
            Dict: configuration instead of credentials.
        """
        match (metrics := self.agent_databases()['metrics'])['type']:
            case 'influxdb':
                return {
                    'type': 'influxdb',
                    'collection_interval': metrics['collectionInterval'],
                    'max_threads': metrics['maxThreads'],
                    'host_connection_timeout': metrics['hostConnectionTimeout'],
                    'trailing': metrics['trailing']
                }
            case _:
                log.error(f'Metrics database type \'{metrics["type"]}\' unsupported')
                sys.exit(1)
"""
Parse config files with the v1alpha1 config-parsing class.
"""


from typing import List
from attrs import define

import logging
import os
import sys


log = logging.getLogger(__name__)

__all__ = [
    'Config'
]


@define
class DatabaseCredentials:
    """
    Database credentials.
    """
    username: str
    password: str


@define
class Connection:
    """
    Connection configuration options.
    """
    url: str
    database: str
    credentials: DatabaseCredentials

    def __attrs_post_init__(self):
        """
        Post-initialization method to expand environment variables.
        """
        self.expand()

    def expand(self):
        """
        Expand environment variables in the connection configuration.
        """
        self.url = os.path.expandvars(self.url)
        self.database = os.path.expandvars(self.database)
        self.credentials.username = os.path.expandvars(self.credentials.username)
        self.credentials.password = os.path.expandvars(self.credentials.password)


@define
class State:
    """
    State database configuration options.
    """
    type: str
    collectionInterval: int
    connection: Connection


@define
class Metrics:
    """
    Metrics database configuration options.
    """
    type: str
    connection: Connection
    collectionInterval: int
    maxThreads: int
    hostConnectionTimeout: int
    trailing: int


@define
class Databases:
    """
    Databases configuration options.
    """
    state: State
    metrics: Metrics


@define
class Platform:
    """
    Platform configuration options.
    """
    host: str
    token: str
    cacert: str
    actionsQueueMaxSize: int

    def __attrs_post_init__(self):
        """
        Post-initialization method to expand environment variables.
        """
        self.expand()

    def expand(self):
        """
        Expand environment variables in the platform configuration.
        """
        self.host = os.path.expandvars(self.host)
        self.token = os.path.expandvars(self.token)
        self.cacert = os.path.expandvars(self.cacert)


@define
class Reconciliation:
    """
    Reconciliation configuration options.
    """
    interval: int


@define
class Autoscale:
    """
    Autoscale configuration options.
    """
    hosts: List
    groups: List


@define
class Controller:
    """
    Controller configuration options.
    """
    databases: Databases
    platform: Platform
    reconciliation: Reconciliation
    autoscale: Autoscale


@define
class Config:
    """
    Parse config files of version v1alpha1.
    """
    version: str
    controller: Controller


# class Config_v1alpha1(Config):
#     """
#     Class that encapsulates access methods and parsing config version v1alpha1.
#     """

#     # Top-level.

#     def controller(self) -> Dict:
#         """
#         Get the controller config dict.

#         Returns:
#             Dict: the controller config dict.
#         """
#         return self.config['controller']

#     def autoscale(self) -> Dict:
#         """
#         Get the autoscale config dict.

#         Returns:
#             Dict: _description_
#         """
#         return self.config['autoscaling']

#     ## Secondary-level.

#     def controller_daemon(self) -> Dict:
#         """
#         Get the daemon configuration options as a flat map.

#         Returns:
#             Dict: The daemon configuration options.
#         """
#         return self.controller()['daemon']

#     def controller_databases(self) -> Dict:
#         """
#         Get the autoscaling databases configuration map.

#         Returns:
#             Dict: The autoscale.databases config map.
#         """
#         return self.controller()['databases']

#     def autoscale_hosts(self) -> Dict:
#         """
#         Get the host groups list from the autoscaling map.

#         Returns:
#             Dict: The host groups list.
#         """
#         return self.autoscale()['hosts']

#     def autoscale_groups(self) -> Dict:
#         """
#         Get the autoscaling groups list from the autoscaling map.

#         Returns:
#             Dict: The autoscaling groups list.
#         """
#         return self.autoscale()['groups']

#     ### Databases

#     #### state

#     def controller_databases_state_connection(self) -> Dict:
#         """
#         Get the state database credentials (MySQL).

#         Returns:
#             Dict: MySQL configuration and credentials.
#         """
#         match (state := self.controller_databases()['state'])['type']:
#             case 'mysql':
#                 mysql_connect = state['connection']
#                 return {
#                     'type': 'mysql',
#                     'url': os.path.expandvars(mysql_connect['url']),
#                     'database': os.path.expandvars(mysql_connect['database']),
#                     'username': os.path.expandvars(mysql_connect['credentials']['username']),
#                     'password': os.path.expandvars(mysql_connect['credentials']['password'])
#                 }
#             case _:
#                 log.error(f'State database type \'{state["type"]}\' unsupported')
#                 sys.exit(1)

#     def controller_databases_state_configuration(self) -> Dict:
#         """
#         Get the state database credentials (MySQL).

#         Returns:
#             Dict: MySQL configuration and credentials.
#         """
#         match (state := self.controller_databases()['state'])['type']:
#             case 'mysql':
#                 return {
#                     'type': 'mysql',
#                     'reconcile_interval': state['reconcileInterval']
#                 }
#             case _:
#                 log.error(f'State database type \'{state["type"]}\' unsupported')
#                 sys.exit(1)

#     #### metrics

#     def controller_databases_metrics_connection(self) -> Dict:
#         """
#         Get the metrics database credentials (InfluxDB).

#         Returns:
#             Dict: Metrics database credentials.
#         """
#         match (metrics := self.controller_databases()['metrics'])['type']:
#             case 'influxdb':
#                 influxdb_connect = metrics['connection']
#                 return {
#                     'type': 'influxdb',
#                     'url': os.path.expandvars(influxdb_connect['url']),
#                     'database': os.path.expandvars(influxdb_connect['database']),
#                     'username': os.path.expandvars(influxdb_connect['credentials']['username']),
#                     'password': os.path.expandvars(influxdb_connect['credentials']['password'])
#                 }
#             case _:
#                 log.error(f'Metrics database type \'{metrics["type"]}\' unsupported')
#                 sys.exit(1)

#     def controller_databases_metrics_configuration(self) -> Dict:
#         """
#         Get the metrics database configuration (whereas the last method retrieved the credentials/auth data).

#         Returns:
#             Dict: configuration instead of credentials.
#         """
#         match (metrics := self.controller_databases()['metrics'])['type']:
#             case 'influxdb':
#                 return {
#                     'type': 'influxdb',
#                     'collection_interval': metrics['collectionInterval'],
#                     'max_threads': metrics['maxThreads'],
#                     'host_connection_timeout': metrics['hostConnectionTimeout'],
#                     'trailing': metrics['trailing']
#                 }
#             case _:
#                 log.error(f'Metrics database type \'{metrics["type"]}\' unsupported')
#                 sys.exit(1)
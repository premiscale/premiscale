"""
Parse config files with the v1alpha1 config-parsing class.
"""


from typing import Optional, Any
from premiscale.config._config import Config

import logging


log = logging.getLogger(__name__)


class Config_v1_alpha_1(Config):
    """
    Config parser for v1a1.
    """

    # Top-level config items.

    def agent(self) -> 'Config_v1_alpha_1':
        """
        Get the agent top-level item.
        """
        return self.config.agent    # type: ignore

    def scaling(self) -> 'Config_v1_alpha_1':
        """
        Get the scaling top-level item.
        """
        return self.config.scaling  # type: ignore

    # hostGroups

    def hostGroups(self) -> 'Config_v1_alpha_1':
        """
        Retrieve a map of hostgroups.
        """
        return self.config.scaling.hostGroups  # type: ignore

    def hostGroupLookup(self, name: str) -> Optional['Config_v1_alpha_1']:
        """
        Perform a host group lookup. Return the group if it's found, None otherwise.
        """
        for group in self.hostGroups():
            if group == name:
                return self.hostGroups()[group]
        return None

    # ASGs

    def autoscalingGroups(self) -> 'Config_v1_alpha_1':
        """
        Retrieve autoscaling groups configuration.
        """
        return self.scaling.autoscalingGroups  # type: ignore

    def autoscalingGroupLookup(self, name: str) -> Optional['Config_v1_alpha_1']:
        """
        Perform an ASG lookup. Return the group if it's found, None otherwise.
        """
        for asg in self.autoscalingGroups():
            if asg == name:
                return self.autoscalingGroups()[asg]
        return None

    # Databases

    def stateDatabase(self) -> 'Config_v1_alpha_1':
        """
        Retrieve info about the state (MySQL) database.
        """
        return self.scaling.databases.state    # type: ignore

    def stateDatabaseCredentials(self) -> 'Config_v1_alpha_1':
        """
        Retrieve info about the state (MySQL) database credentials.
        """
        return self.scaling.databases.state.connection.credentials.env    # type: ignore

    def stateDatabaseConnection(self) -> str:
        """
        Get the connection string for the state database.
        """
        return str(self.scaling.databases.state.connection.url)    # type: ignore

    def metricsDatabase(self) -> 'Config_v1_alpha_1':
        """
        Retrieve info about the metrics (InfluxDB) database.
        """
        return self.scaling.databases.metrics  # type: ignore

    def metricsDatabaseCredentials(self) -> 'Config_v1_alpha_1':
        """
        Retrieve info about the metrics (InfluxDB) database.
        """
        return self.scaling.databases.metrics.connection.credentials.env  # type: ignore

    def metricsDatabaseConnection(self) -> str:
        """
        Get the connection string for the metrics database.
        """
        return str(self.scaling.databases.metrics.connection.url)  # type: ignore

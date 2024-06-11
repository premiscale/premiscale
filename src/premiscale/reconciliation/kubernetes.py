"""
Interface with the Kubernetes autoscaler.
"""


import logging

from typing import Any
from setproctitle import setproctitle
from premiscale.config.v1alpha1 import Config


log = logging.getLogger(__name__)


class KubernetesAutoscaler:
    def __init__(self, config: Config) -> None:
        pass

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        log.debug('Starting Kubernetes autoscaler interface subprocess')
        setproctitle('kubernetes-autoscaler-interface')
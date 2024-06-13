"""
Interface with the Kubernetes autoscaler.
"""


from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from setproctitle import setproctitle


if TYPE_CHECKING:
    from typing import Any
    from premiscale.config.v1alpha1 import Config


log = logging.getLogger(__name__)


class KubernetesAutoscaler:
    def __init__(self, config: Config) -> None:
        pass

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        log.debug('Starting Kubernetes autoscaler interface subprocess')
        setproctitle('kubernetes-autoscaler-interface')
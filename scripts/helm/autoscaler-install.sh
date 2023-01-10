#! /usr/bin/env bash
# Install autoscaler to the platform-develop namespace.


NAMESPACE="${1:-platform-develop}"


(
    cd helm/autoscaler || exit 1 && \
    helm dependency build && \
    helm upgrade --install --namespace "$NAMESPACE" --create-namespace autoscaler . --values values.yaml
)
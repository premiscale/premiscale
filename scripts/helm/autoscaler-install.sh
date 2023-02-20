#! /usr/bin/env bash
# Install PremiScale autoscaler to the platform-develop namespace.


NAMESPACE="${1:-platform-develop}"


(
    cd helm/premiscale || exit 1 && \
    helm dependency build && \
    helm upgrade --install --namespace "$NAMESPACE" --create-namespace premiscale . --values values.yaml
)
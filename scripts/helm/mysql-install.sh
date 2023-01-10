#! /usr/bin/env bash
# Install MySQL to the platform-develop namespace.


NAMESPACE="${1:-platform-develop}"


(
    cd helm/mysql || exit 1 && \
    helm dependency build && \
    helm upgrade --install --namespace "$NAMESPACE" --create-namespace mysql . --values values.yaml
)
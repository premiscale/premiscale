#! /usr/bin/env bash
# Install InfluxDB to the platform-develop namespace.


NAMESPACE="${1:-platform-develop}"


(
    cd helm/influxdb || exit 1 && \
    helm dependency build && \
    helm upgrade --install --namespace "$NAMESPACE" --create-namespace influxdb . --values values.yaml
)
#! /usr/bin/env bash
# Install the PremiScale agent Helm chart.


VERSION="${1}"
NAMESPACE="${2:-agent-develop}"


if [ $# -ne 1 ]; then
    printf "Expected at least 1 arg: version, namespace.\\n" >&2
    exit 1
fi


(
    cd helm/premiscale || exit 1 && \
    helm dependency build && \
    helm upgrade --install --namespace "$NAMESPACE" --create-namespace premiscale premiscale-develop/premiscale --version "$VERSION" --values values.yaml
)
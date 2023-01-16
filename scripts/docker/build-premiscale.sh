#! /usr/bin/env bash
# Docker build of the docker/autoscaler-directory.

PYTHON_PACKAGE_VERSION="${1:-0.0.1a287}"
PYTHON_USERNAME="$(pass show premiscale/nexus/username)"
PYTHON_PASSWORD="$(pass show premiscale/nexus/password)"
PYTHON_REPOSITORY="${2:-python-develop}"


docker build . -t docker.ops.premiscale.com/premiscale:"$PYTHON_PACKAGE_VERSION" --build-arg=PYTHON_PACKAGE_VERSION="$PYTHON_PACKAGE_VERSION" --build-arg=PYTHON_USERNAME="$PYTHON_USERNAME" --build-arg=PYTHON_PASSWORD="$PYTHON_PASSWORD" --build-arg=PYTHON_REPOSITORY="$PYTHON_REPOSITORY" -f docker/autoscaler/Dockerfile
#! /usr/bin/env bash
# Docker build of the docker/autoscaler-directory.

VERSION="${1:-0.0.1a285}"
PYTHON_USERNAME="$(pass show premiscale/nexus/username)"
PYTHON_PASSWORD="$(pass show premiscale/nexus/password)"


docker build . -t docker.ops.premiscale.com/premiscale:"$VERSION" --build-arg=VERSION="$VERSION" --build-arg=PYTHON_USERNAME="$PYTHON_USERNAME" --build-arg=PYTHON_PASSWORD="$PYTHON_PASSWORD" -f docker/autoscaler/Dockerfile
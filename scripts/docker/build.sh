#! /usr/bin/env bash
# Docker build of the docker/PROJECT-directory.

PROJECT="${1:-autoscaler}"
VERSION="${2:-0.1.0}"


docker build . -t docker.ops.premiscale.com/"$PROJECT":"$VERSION" --build-arg=VERSION="$VERSION" -f docker/"$PROJECT"/Dockerfile
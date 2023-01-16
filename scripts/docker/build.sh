#! /usr/bin/env bash
# Docker build of the docker/PROJECT-directory.

PROJECT="${1:-premiscale}"
VERSION="${2:-0.0.1a285}"


docker build . -t docker.ops.premiscale.com/"$PROJECT":"$VERSION" --build-arg=VERSION="$VERSION" -f docker/"$PROJECT"/Dockerfile
#! /usr/bin/env bash
# Docker run the docker/PROJECT-directory.

PROJECT="${1:-autoscaler}"
VERSION="${2:-0.1.0}"
shift && shift


docker run -itd --name "$PROJECT" docker.ops.premiscale.com/"$PROJECT":"$VERSION" "$@"
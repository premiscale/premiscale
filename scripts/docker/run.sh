#! /usr/bin/env bash
# Docker run the docker/PROJECT-directory.

PROJECT="${1:-premiscale}"
VERSION="${2:-0.1.0}"
shift && shift


# docker run -itd --name "$PROJECT" docker.ops.premiscale.com/"$PROJECT":"$VERSION" "$@"

docker stop premiscale && docker rm premiscale
docker run -itd --name "${PROJECT}" -e DOPPLER_TOKEN="$(pass show premiscale/doppler/development-service-token)" -e PREMISCALE_DEBUG=true docker-develop.ops.premiscale.com/"${PROJECT}":"${VERSION}" "$@"
docker exec -it "${PROJECT}" /bin/bash
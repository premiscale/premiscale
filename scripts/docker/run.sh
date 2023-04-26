#! /usr/bin/env bash
# Docker run the docker/PROJECT-directory.


VERSION="${1:-0.1.0}"
COUNT="${2:-1}"
PROJECT="${3:-premiscale}"
shift && shift && shift


mapfile -t containers < <(docker ps --format '{{.Names}}' | grep "$PROJECT")
for container in "${containers[@]}"; do
    docker stop "$container" >/dev/null && docker rm "$container" >/dev/null && printf "Removed running container \"%s\"\\n" "$container"
done


for _ in $(seq 1 "$COUNT"); do
    docker run -itd --name "${PROJECT}"-"$(uuid | sed "s@-@@g" | head -c 10)" \
        -e DOPPLER_TOKEN="$(pass show premiscale/doppler/development-service-token)" \
        -e PREMISCALE_DEBUG=true \
        -e PREMISCALE_TOKEN=123 \
        docker-develop.ops.premiscale.com/"${PROJECT}":"${VERSION}" "$@"
done
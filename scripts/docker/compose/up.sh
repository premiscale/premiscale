#! /usr/bin/env bash
# Docker compose up of the docker/-directory.

(
    cd docker/ || exit 1 && \
    DOPPLER_TOKEN="$(pass show premiscale/doppler/production-service-token)" docker compose up -d --build
)

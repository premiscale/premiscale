#! /usr/bin/env bash
# Bring up a fresh instance of the docker compose stack.

docker compose -f compose.yaml down

if command -v clear_containers &>/dev/null; then
    printf "Clearing all containers...\\n"
    clear_containers
fi
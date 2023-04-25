#! /usr/bin/env bash
# Get the process tree on a docker container.

if [ $# -ne 1 ]; then
    printf "Must provided a container name to run ps against.\\n" >&2
    exit 1
fi

CONTAINER="${1}"

docker exec -it "$CONTAINER" ps -ef --forest
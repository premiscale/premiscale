#! /usr/bin/env bash
# Show threads on a process in a docker container.

if [ $# -ne 1 ]; then
    printf "Must provided a PID and a container name to run ps against.\\n" >&2
    exit 1
fi

PID="${1}"
CONTAINER="${2:-premiscale}"

docker exec -it "$CONTAINER" ps -T -p "$PID"
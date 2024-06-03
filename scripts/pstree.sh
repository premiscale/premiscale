#! /usr/bin/env bash
# Get the process tree on a pod.

POD="${1:-premiscale}"

docker exec -it "$POD" ps -ef --forest
#kubectl exec -it "$POD" -- /bin/bash -c 'ps -ef --forest'
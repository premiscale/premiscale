#! /usr/bin/env bash
# Bring up a fresh instance of the docker compose stack.

docker compose -f compose.yaml down


# clear_containers()
# {
#     mapfile -t CONTAINERS < <(sudo docker ps -a | awk '{ print $1 }' | tail -n +2)

#     for c in "${CONTAINERS[@]}"; do
#         sudo docker rm "$c"
#     done

#     mapfile -t IMAGES < <(sudo docker images | awk '{ print $3 }' | tail -n +2)

#     for im in "${IMAGES[@]}"; do
#         sudo docker rmi "$im"
#     done
# }


# clear_containers
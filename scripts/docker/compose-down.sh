#! /usr/bin/env bash
# Bring up a fresh instance of the docker compose stack.

# Set our profile.
if [ $# -ne 0 ]; then
    PROFILE="$1"
else
    PROFILE="zero"
fi


DOTENV=".env"


function cleanup_dotenv()
{
    if [ -f "$DOTENV" ]; then
        rm "${DOTENV:?}"
    fi
}


# Write a temporary .env-file, since docker-compose likes to live in the past.
cleanup_dotenv
printf "INFO: Decrypting secrets for %s-file\\n" "$DOTENV"
cat <<EOF > "$DOTENV"
PREMISCALE_TEST_SSH_KEY="$(pass show premiscale/doppler/ssh/chelsea-hosts-test)"
EOF

docker compose --profile="$PROFILE" -f compose.yaml down
cleanup_dotenv


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
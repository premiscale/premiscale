#! /usr/bin/env bash
# Bring up a fresh instance of the docker compose stack.

# Set our profile.
if [ $# -ne 0 ]; then
    PROFILE="$1"
else
    PROFILE="zero"
fi


DOTENV=".env"


##
# Create a temporary .env-file with decrypted environment variables for docker compose to pick up.
function decrypt_env()
{
    # Decrypt the .env-file.
    printf "INFO: Decrypting secrets for %s-file\\n" "$DOTENV"
cat <<EOF > "$DOTENV"
PREMISCALE_TEST_SSH_KEY="$(pass show premiscale/doppler/ssh/chelsea-hosts-test)"
EOF

    return 0
}


##
# Cleanup the temporary .env-file.
function cleanup_env()
{
    if [ -f "$DOTENV" ]; then
        rm "${DOTENV:?}"
    fi
}


if [ ! -f ".env" ]; then
    decrypt_env
fi


docker compose --profile="$PROFILE" -f compose.yaml down


cleanup_env


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
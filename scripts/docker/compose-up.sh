#! /usr/bin/env bash
# Bring up a fresh instance of the docker-compose orchestrated stack.

set -o pipefail
shopt -s nullglob extglob


# Set our profile.
if [ $# -ne 0 ]; then
    PROFILE="$1"
else
    PROFILE="zero"
fi

DOTENV=".env"


##
# Cleanup the temporary .env-file.
function cleanup_env()
{
    if [ -f "$DOTENV" ]; then
        rm "${DOTENV:?}"
    fi
}


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


# Cleanup previous stacks.
./scripts/docker/compose-down.sh "$PROFILE"

# Reset the environment.
cleanup_env

# Decrypt the environment variables.
decrypt_env


# Generate self-signed certificates if they don't exist.
if [ ! -d "certs/" ]; then
    mkdir certs/
    # https://medium.com/@maciej.skorupka/hostname-mismatch-ssl-error-in-python-2901d465683
    openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -sha256 -days 10 -nodes -subj "/C=US/ST=Massachusetts/L=Chelsea/O=PremiScale/CN=platform/emailAddress=$(git config --global --get user.email)" -addext "subjectAltName=DNS:platform,DNS:grafana"
fi


COMPOSE_DOCKER_CLI_BUILD=1
export COMPOSE_DOCKER_CLI_BUILD

DOCKER_BUILDKIT=1
export DOCKER_BUILDKIT


##
# Reverse lookup the controller name for a given profile.
function reverse_lookup_profile()
{
    if [ $# -ne 1 ]; then
        printf "ERROR: Function \"reverse_lookup_profile\" expects exactly one argument: Docker compsoe profile name.\\n" >&2
        exit 1
    fi

    local controller profile

    profile="$1"
    mapfile -t controller < <(yq ".services | to_entries | .[] | select(.value.profiles[0] == \"$profile\") | .key" compose.yaml)

    if [ "${#controller[@]}" -eq 0 ]; then
        printf "ERROR: Could not find a controller for the profile \"%s\".\\n" "$1" >&2
        exit 1
    elif [ "${#controller[@]}" -gt 1 ]; then
        printf "ERROR: Found multiple controllers for the profile \"%s\": %s.\\n" "$1" "${controller[*]}" >&2
        exit 1
    fi

    printf "%s" "${controller[0]}"

    return 0
}


docker compose \
    --profile "$PROFILE" \
    -f compose.yaml up \
    -d --build "$(reverse_lookup_profile "$PROFILE")" platform echoes registration


cleanup_env
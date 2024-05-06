#! /usr/bin/env bash
# Bring up a fresh instance of the docker compose stack.

./scripts/docker/compose-down.sh

# Generate self-signed certificates if they don't exist.
if [ ! -d "certs/" ]; then
    mkdir certs/
    # https://medium.com/@maciej.skorupka/hostname-mismatch-ssl-error-in-python-2901d465683
    openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -sha256 -days 10 -nodes -subj "/C=US/ST=Massachusetts/L=Chelsea/O=PremiScale/CN=platform/emailAddress=$(git config --global --get user.email)" -addext "subjectAltName=DNS:platform"
fi

# docker compose build -f compose.yaml --no-cache
docker compose -f compose.yaml up -d --build premiscale platform echoes registration
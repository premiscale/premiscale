#! /usr/bin/env bash
# Bring up a fresh instance of the docker compose stack.

./scripts/docker/compose-down.sh

# Generate self-signed certificates if they don't exist.
if [ ! -d "certs/" ]; then
    mkdir certs/
    openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -sha256 -days 10 -nodes -subj "/C=XX/ST=MA/L=Chelsea/O=PremiScale/OU=PremiScale/CN=platform"
fi

docker compose -f compose.yaml up -d
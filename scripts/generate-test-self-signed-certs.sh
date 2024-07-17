#! /usr/bin/env bash
# Generate self-signed certificates for local development.


printf "INFO: Generating self-signed certificates for local development.\\n"


function _generate()
{
    # https://medium.com/@maciej.skorupka/hostname-mismatch-ssl-error-in-python-2901d465683
    openssl req \
        -x509 \
        -newkey rsa:4096 \
        -keyout certs/key.pem \
        -out certs/cert.pem \
        -sha256 \
        -days 10 \
        -nodes \
        -subj "/C=US/ST=Massachusetts/L=Chelsea/O=PremiScale/CN=platform/emailAddress=$(git config --global --get user.email)" \
        -addext "subjectAltName=DNS:platform" # ,DNS:grafana"
}


# Generate self-signed certificates if they don't exist.
if [ ! -d "certs/" ]; then
    mkdir certs/
    _generate
elif [ ! -f "certs/cert.pem" ] || [ ! -f "certs/key.pem" ]; then
    _generate
else
    printf "INFO: Self-signed certificates already exist.\\n"
fi
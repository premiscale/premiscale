#! /usr/bin/env bash
# View the contents of the generated self-signed certificate with openssl.

openssl x509 -noout -text < certs/cert.pem | less
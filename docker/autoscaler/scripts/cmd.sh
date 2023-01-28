#! /bin/bash
# Start the backend api.

PREMISCALE_DEBUG="${1:-false}"

# shellcheck disable=SC1091
source bin/activate

if "$PREMISCALE_DEBUG"; then
    premiscale --log-stdout --version --debug
    premiscale --log-stdout --daemon --debug
else
    premiscale --log-stdout --version
    premiscale --log-stdout --daemon
fi

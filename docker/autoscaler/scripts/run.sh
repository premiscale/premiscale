#! /bin/bash
# Start the backend api.

# shellcheck disable=SC1091
source bin/activate

premiscale --log-stdout --version
premiscale --log-stdout --daemon

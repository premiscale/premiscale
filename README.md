# PremiScale

The PremiScale Kubernetes controller brings autoscaling to on-premise infrastructure.

```shell
$ premiscale --help
usage: premiscale [-h] [-d] [-c CONFIG] [--host HOST] [--token TOKEN] [--validate] [--version] [--log-stdout] [--pid-file PID_FILE] [--debug]

PremiScale autoscaler agent. © PremiScale, Inc. 2024

options:
  -h, --help            show this help message and exit
  -d, --daemon          Start PremiScale as a daemon. (default: False)
  -c CONFIG, --config CONFIG
                        Configuration file path to use. (default: /opt/premiscale/config.yaml)
  --host HOST           WSS URL of the PremiScale platform. (default: wss://app.premiscale.com)
  --token TOKEN         Token for registering the agent with the PremiScale platform on first start. (default: )
  --validate            Validate the provided configuration file. (default: False)
  --version             Show premiscale version. (default: False)
  --log-stdout          Log to stdout (for use in containerized deployments). (default: False)
  --pid-file PID_FILE   Pidfile name to use for daemon. (default: /opt/premiscale/premiscale.pid)
  --debug               Turn on logging debug mode. (default: False)

```

## Development

### Local

Run

```shell
docker compose up -d
```

This will bring up a number of services, including platform services that the controller registers and connects to for billing.

### Remote

Connect to your development cluster of choice with kubectl access, followed by

```shell
devspace
```

This will bring up a development stack in a local or remote Kubernetes cluster of your choice.

### Tests

Run unit tests with

```shell
poetry run pytest tests/unit
```

e2e tests against a live environment with

```shell
poetry run pytest tests/e2e
```

And coverage against the codebase with

```shell
poetry run coverage run -m pytest
poetry run coverage report -m pytest
```

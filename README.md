# PremiScale

PremiScale brings autoscaling to on-premise infrastructure, with a particular focus on integrating with the [Kubernetes autoscaler](https://github.com/kubernetes/autoscaler).

```text
$ premiscale --help
usage: premiscale [-h] [-d] [-c CONFIG] [--host HOST] [--token TOKEN] [--validate] [--version] [--log-stdout] [--pid-file PID_FILE] [--debug]

PremiScale autoscaler controller. © PremiScale, Inc. 2024

options:
  -h, --help            show this help message and exit
  -d, --daemon          Start PremiScale as a daemon. (default: False)
  -c CONFIG, --config CONFIG
                        Configuration file path to use. (default: /opt/premiscale/config.yaml)
  --platform PLATFORM   WSS URL of the PremiScale platform. (default: wss://app.premiscale.com)
  --token TOKEN         Token for registering the agent with the PremiScale platform on first start. (default: )
  --validate            Validate the provided configuration file. (default: False)
  --version             Show premiscale version. (default: False)
  --log-stdout          Log to stdout (for use in containerized deployments). (default: False)
  --pid-file PID_FILE   Pidfile name to use for daemon. (default: /opt/premiscale/premiscale.pid)
  --debug               Turn on logging debug mode. (default: False)
```

## Architecture

PremiScale is a controller that works by

See the [architecture diagram](https://drive.google.com/file/d/1hjwaMVQESdU2KffEJ4FpWDC1hjVHCLZX/view?usp=sharing) for PremiScale, or check out the diagram below, for an overview of just the controller.

<p align="center" width="100%">
  <img width="100%" src="img/premiscale-architecture-controller.png" alt="premiscale architecture controller">
</p>

## Development

### Dependencies

Install [asdf](https://asdf-vm.com/guide/getting-started.html#_1-install-dependencies), followed by running `asdf install` in the root of this project.

### Local

```shell
yarn compose:up
```

This will bring up a number of services, including platform services that the controller registers and connects to for billing. When you're finished, run

```shell
yarn compose:down
```

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

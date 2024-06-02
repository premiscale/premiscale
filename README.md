# PremiScale

PremiScale is a controller that brings autoscaling to on-premise infrastructure, with a particular focus on integrating with the [Kubernetes autoscaler](https://github.com/kubernetes/autoscaler).

<!-- [[[cog
import subprocess
import cog

cog.outl(f'```text\n$ premiscale --help\n{subprocess.run("poetry run premiscale --help".split(" "), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode()}\n```')
]]] -->
```text
$ premiscale --help
usage: premiscale [-h] [--token TOKEN] [-d] [-c CONFIG] [--validate]
                  [--platform PLATFORM] [--version] [--pid-file PID_FILE]
                  [--log-level {info,error,warn,debug}]
                  [--log-file LOG_FILE | --log-stdout] [--cacert CACERT]

PremiScale autoscaler. © PremiScale, Inc. 2024

options:
  -h, --help            show this help message and exit
  --token TOKEN         Platform registration token. (default: )
  -d, --daemon          Start controller as a daemon. (default: False)
  -c CONFIG, --config CONFIG
                        Configuration file path to use. (default:
                        /opt/premiscale/config.yaml)
  --validate            Validate the provided configuration file and exit.
                        (default: False)
  --platform PLATFORM   URL of the PremiScale platform. (default:
                        app.premiscale.com)
  --version             Display controller version. (default: False)
  --pid-file PID_FILE   Pidfile name to use for the controller daemon.
                        (default: /opt/premiscale/premiscale.pid)
  --log-level {info,error,warn,debug}
                        Set the logging level. (default: info)
  --log-file LOG_FILE   Specify the file the service logs to if --log-stdout
                        is not set. (default: /opt/premiscale/controller.log)
  --log-stdout          Log to stdout (for use in containerized deployments).
                        (default: False)
  --cacert CACERT       Path to the certificate file (for use with self-signed
                        certificates). (default: )

```
<!-- [[[end]]] (checksum: 581a2399ae1ce56b76349ea501875d4a) (checksum: ) -->

## Architecture

PremiScale is a controller (or agent, depending on how you look at it) that administers virtual machine hosts and virtual machines by leveraging [libvirt](https://libvirt.org/). Libvirt is a stable (open source) hypervisor SDK and interface.

See the [architecture diagram](https://drive.google.com/file/d/1hjwaMVQESdU2KffEJ4FpWDC1hjVHCLZX/view?usp=sharing) for PremiScale, or check out the diagram below, for an overview of just the controller.

<p align="center" width="100%">
  <img width="100%" src="img/premiscale-architecture-controller.png" alt="premiscale architecture controller">
</p>

## Installation

See the [chart README](https://github.com/premiscale/premiscale/tree/master/helm/premiscale) for an overview of controller installation and configuration options.

## Development

### Dependencies

Install [asdf](https://asdf-vm.com/guide/getting-started.html#_1-install-dependencies), followed by running `asdf install` in the root of this project.

### Docker Compose

> **Note:** Some tweaks may need to be made to the repository's [compose.yaml](./compose.yaml) file to get the stack to run on your system.

```shell
yarn compose:up
```

This will bring up a number of local services for running the agent. To tear the stack down, simply run

```shell
yarn compose:down
```

### Remote

Connect to your development cluster of choice with kubectl access, followed by

```shell
devspace
```

This will bring up a development stack in a local or remote Kubernetes cluster of your choice. To start a local development minikube cluster for deploying the devspace stack to, run

```shell
yarn minikube:up
```

This cluster is also used for [running e2e tests](#end-to-end-tests), locally.

### Unit tests

Run unit tests with

```shell
yarn test:unit
```

### End-to-end tests

Run e2e tests against a live (local) environment with

```shell
yarn test:e2e
```

This command will

1. Stand up a local 1-node minikube cluster with 4 cores, 4GiB memory and 30GiB storage. *(Modify [./scripts/minikube.sh](./scripts/minikube.sh) if these resources are unsuitable for your local development environment.)*
2. Create a `localhost` docker registry redirect container.
3. Build both e2e (hosts a git repository with encrypted pass secrets that match paths found in [./src/test/data/crd](./src/test/data/crd/)) and operator container images, as well as push these images to the local redirect for minikube to access.
4. Installs both e2e and pass-operator Helm charts.
5. Run e2e tests.
6. Tear down the cluster and local registry, as well as cleans up locally-built artifacts.

### Coverage

Test coverage against the codebase with

```shell
poetry run coverage run -m pytest
poetry run coverage report -m pytest
```

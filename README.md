# PremiScale

![GitHub Release](https://img.shields.io/github/v/release/premiscale/premiscale?include_prereleases&sort=semver&display_name=release&link=https%3A%2F%2Fgithub.com%2Fpremiscale%2Fpremiscale%2Freleases)
![Business License 1.1](https://img.shields.io/badge/License-Business_Source_1.1-red)

PremiScale is a controller that brings autoscaling of virtual and physical infrastructure to local, self-hosted and private datacenters, with a particular focus on integrating with the Kubernetes [autoscaler](https://github.com/kubernetes/autoscaler).

## Architecture

PremiScale uses [libvirt](https://libvirt.org/) to connect to hosts and manage lifecycles of virtual machines.

The controller can be configured to run in two different modes, including a `kubernetes` (the default) and a `standalone` mode.

### Kubernetes

Starting the controller in `kubernetes` mode (the default) starts relevant components of the controller that allow it to interface with the cluster autoscaler.

<p align="center" width="100%">
  <img width="100%" src="img/premiscale-architecture-controller_internal_autoscaler_disabled.png" alt="premiscale architecture: internal autoscaler disabled">
</p>

### Standalone

In `standalone` mode, the controller starts its own time series data collection process. Users are required to provide a list of hosts on which virtual machines can be created. Users are also required to provide a list of autoscaling groups into which virtual machines the controller manages are organized.

<p align="center" width="100%">
  <img width="100%" src="img/premiscale-architecture-controller_internal_autoscaler_enabled.png" alt="premiscale architecture: internal autoscaler enabled">
</p>

## Configuration

The controller is configured in a couple ways, including its command line interface, environment variables (as indicated in the help text below), and through the required config file (all versions of which are documented [here](./src/premiscale/config/docs/README.md) in this repository).

<!-- [[[cog
import subprocess
import cog

cog.outl(f'```text\n$ premiscale --help\n{subprocess.run("poetry run premiscale --help".split(" "), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode()}\n```')
]]] -->
```text
$ premiscale --help

```
<!-- [[[end]]] (checksum: 8cebe6abdefb1648e599b1c9ea8c441d) (checksum: ) -->

## Installation

This project is intended to be deployed to Kubernetes, whether you intend to integrate with the cluster autoscaler or not.

See the Helm [chart README](https://github.com/premiscale/premiscale/tree/master/helm/premiscale) for an overview of controller installation.
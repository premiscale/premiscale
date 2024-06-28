# PremiScale

![GitHub Release](https://img.shields.io/github/v/release/premiscale/premiscale?include_prereleases&sort=semver&display_name=release&link=https%3A%2F%2Fgithub.com%2Fpremiscale%2Fpremiscale%2Freleases)
![Business License 1.1](https://img.shields.io/badge/License-Business_Source_1.1-red)


PremiScale is a controller that brings autoscaling of virtual and physical infrastructure to local, self-hosted and private data centers, with a particular focus on integrating with the Kubernetes cluster [autoscaler](https://github.com/kubernetes/autoscaler).

## Architecture

PremiScale uses [libvirt](https://libvirt.org/) to connect to hosts and manage lifecycles of virtual machines. The Libvirt daemon provides a rich API for interacting with hypervisors, hosts and virtual machines.

The controller can be configured to run in two different modes, including `kubernetes` (the default) and `standalone` modes. In either configuration, the controller aims to start only relevant processes for both data collection and managing virtual machines. Users are required at this time to provide a list of hosts on which virtual machines can be created, in addition to a list of autoscaling groups, into which virtual machines the controller manages, are organized.

### Standalone

In `standalone` mode (the default), the controller starts its own time series data collection process.

<p align="center" width="100%">
  <img width="100%" src="https://raw.githubusercontent.com/premiscale/premiscale/master/img/premiscale-architecture-controller_internal_autoscaler_enabled.png" alt="premiscale architecture: internal autoscaler enabled">
</p>

### Kubernetes

Starting the controller in `kubernetes` mode starts relevant components of the controller that allow it to interface with the cluster autoscaler.

<p align="center" width="100%">
  <img width="100%" src="https://raw.githubusercontent.com/premiscale/premiscale/master/img/premiscale-architecture-controller_internal_autoscaler_disabled.png" alt="premiscale architecture: internal autoscaler disabled">
</p>

Note that, in this configuration, the controller does not require a time series database. State is still reconciled, but the time series signal comes from the cluster autoscaler instead.

## Configuration

The controller is configured in a couple ways, including its command line interface, environment variables (as indicated in the help text below), and through the required config file (all versions of which are documented [here](https://github.com/premiscale/premiscale/tree/master/src/premiscale/config/docs) in this repository).

## Installation

This project is intended to be deployed to Kubernetes, whether you intend to integrate with the cluster autoscaler or not.

See the Helm [chart README](https://github.com/premiscale/premiscale/tree/master/helm/premiscale) for an overview of controller installation.
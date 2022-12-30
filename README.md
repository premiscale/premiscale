# libvirt autoscaler

This project is a PoC for autoscaling via [libvirt](https://libvirt.org/) virtual machines (primarily KVM-based).

At the time I've started this project, while most public clouds offer autoscaling controllers, there don't appear to be _any_ open source initiatives, let alone one that utilizes the libvirt API. It's my opinion that many on-premise clouds may benefit from such a controller.

## Design

At this time, I'm hoping to cover the following items with an initial v0.1.0-release.

1. Collect metrics for disk IO, CPU and memory, provided by the libvirt API, and form a decision, based on a configuration file in YAML format /etc/autoscaler/autoscale.yaml, whether or not to scale up or down, or wait an additional configured period before the daemon checks in on these metrics again.

2. Provision new VMs on a list of hosts, reachable with the libvirt API.
    - Eventually, a strategy should be respected for placing VMs, such as round-robin (rr), resource-based (free resources) i.e. the host with the most free CPU, memory and disk IO should be selected), or first-come-first-utilized, so hosts are used one-by-one as necessary. Eventually, it would be neat if plugins could be used with this tool to control hosts as well (or maybe that's for a separate tool altogether).

3. A well-defined process should be laid out (maybe I should create a wiki for this project) for pairing libvirt domains with cloud-init scripts, so VMs can be customized before instantiation (cloud-init scripts updated) and VMs can be customized during boot. Networking at a minimum?

### Virtual disks

Disk images should be generalized with `virt-sysprep` and bundled with cloud-init scripts for customization.

### Databases

I'm thinking this tool should use at most two databases, including an influxdb time-series db for VM metrics, and a SQL database (probably just MySQL) for storing state. Both can easily be deployed as statefulsets on a k8s cluster, and they can certainly be deployed on a host of their own.

## Additional ideas / thoughts

1. A Flask endpoint should be available for VMs to authenticate and check in to make sure they're still healthy? Or even to check in when they're finally up.
2. What does DR look like if the autoscaling daemon goes down. We should be able to start it up again, since
all state is stored in a MySQL database.

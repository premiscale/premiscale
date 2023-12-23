# PremiScale

```shell
$ premiscale --help
usage: premiscale [-h] [-d] [-c CONFIG] [--host HOST] [--token TOKEN] [--validate] [--version] [--log-stdout] [--pid-file PID_FILE] [--debug]

PremiScale autoscaler agent. © PremiScale, Inc. 2023

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

The PremiScale agent can be used to autoscale virtual machines and manage hardware in an on-premise datacenter (or a developer's local machine).

## TODOs

1. A well-defined process should be laid out (maybe I should create a wiki for this project) for pairing libvirt domains with cloud-init scripts, so VMs can be customized before instantiation (cloud-init scripts updated) and VMs can be customized during boot. Networking at a minimum?

### Databases

I'm thinking this tool should use at most two databases, including an influxdb time-series db for VM metrics, and a SQL database (probably just MySQL) for storing state. Both can easily be deployed as statefulsets on a k8s cluster, and they can certainly be deployed on a host of their own.

## Additional ideas / thoughts

1. A Flask endpoint should be available for VMs to authenticate and check in to make sure they're still healthy? Or even to check in when they're finally up.
2. What does DR look like if the autoscaling daemon goes down. We should be able to start it up again, since
all state is stored in a MySQL database.
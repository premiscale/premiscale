# PremiScale

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

The PremiScale agent can be used to autoscale virtual machines and manage hardware in an on-premise datacenter (or a developer's local machine).
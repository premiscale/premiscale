# PremiScale controller configuration

Local controller config versions are documented here. When a controller with no user-provided config starts for the first time, a default config is created, which always reflects the latest version available as of the release.

- [`default`](./default.md): the [default.yaml](./../default.yaml) that's created when no user-provided config is found.
- [`v1alpha1`](./v1alpha1.md)

## Controller CLI

<!-- [[[cog
import subprocess
import cog

cog.outl(f'```text\n$ premiscale --help\n{subprocess.run("poetry run premiscale --help".split(" "), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode()}\n```')
]]] -->
```text
$ premiscale --help
usage: premiscale [-h] [--token TOKEN] [-c CONFIG] [--validate] [--version]
                  [--log-level {info,error,warn,debug}]
                  [--log-file LOG_FILE | --log-stdout]

The PremiScale autoscaling controller for Kubernetes.

options:
  -h, --help            show this help message and exit
  --token TOKEN         Platform registration token. Also available as the
                        environment variable 'PREMISCALE_TOKEN'. If no token
                        is provided, the controller will not register with the
                        platform and start in standalone mode.
  -c CONFIG, --config CONFIG
                        Configuration file path to use. Also available as the
                        environment variable 'PREMISCALE_CONFIG_PATH'.
                        (default: /opt/premiscale/config.yaml)
  --validate            Validate the provided configuration file and exit.
                        (default: false)
  --version             Display controller version.
  --log-level {info,error,warn,debug}
                        Set the logging level. Also available as the
                        environment variable 'PREMISCALE_LOG_LEVEL'. (default:
                        info)
  --log-file LOG_FILE   Specify the file the service logs to if --log-stdout
                        is not set. Also available as the environment variable
                        'PREMISCALE_LOG_FILE'. (default:
                        /opt/premiscale/controller.log)
  --log-stdout          Log to stdout (for use in containerized deployments).
                        (default: false)

For more information, visit https://premiscale.com.

© PremiScale, Inc. 2024.

```
<!-- [[[end]]] (checksum: 83576b46aefcfd04dba8baa176fd05ff) (checksum: ) -->

## Validating configuration files

Validate a config file with the following command.

```shell
premiscale --config src/premiscale/config/default.yaml --validate --log-stdout
```
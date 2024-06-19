# `default.yaml`

## Parameters

### Controller Configuration

| Name                                   | Description                                                                                                                                                                                                                                                    | Value                            |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `controller.pidFile`                   | Path to the file where the controller daemon process writes its PID.                                                                                                                                                                                           | `/opt/premiscale/premiscale.pid` |
| `controller.mode`                      | The mode of the controller. Can be 'kubernetes' or 'standalone'. If 'standalone', the controller will not attempt to connect to a Kubernetes cluster autoscaler. If 'kubernetes', the controller will attempt to connect to the Kubernetes cluster autoscaler. | `standalone`                     |
| `controller.kubernetes.autoscalerPort` | The port on which the Kubernetes autoscaler is listening.                                                                                                                                                                                                      | `8080`                           |
| `controller.kubernetes.autoscalerHost` | The host on which the Kubernetes autoscaler is running. See also the cluster autoscaler Helm chart: https://github.com/premiscale/kubernetes-autoscaler/tree/master/charts/cluster-autoscaler.                                                                 | `cluster-autoscaler`             |

### Healthcheck Configuration

| Name                          | Description                                            | Value       |
| ----------------------------- | ------------------------------------------------------ | ----------- |
| `controller.healthcheck`      | Configure the healthcheck endpoint for the controller. | `{}`        |
| `controller.healthcheck.host` | The host to bind the healthcheck endpoint to.          | `127.0.0.1` |
| `controller.healthcheck.port` | The port to bind the healthcheck endpoint to.          | `8085`      |

### Database Configuration

| Name                                            | Description                                                                                                 | Value                           |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------- |
| `controller.databases.maxHostConnectionThreads` | The maximum number of threads to use for connecting to hosts.                                               | `10`                            |
| `controller.databases.collectionInterval`       | How often the agent retrieves state from all of the connected hosts.                                        | `60`                            |
| `controller.databases.hostConnectionTimeout`    | How long to wait for a connection to a host before timing out.                                              | `60`                            |
| `controller.databases.state.type`               | The type of database to use for storing state. Can be 'mysql' or 'sqlite' or 'memory'.                      | `memory`                        |
| `controller.databases.timeseries.type`          | The type of database to use for storing time series data. At this time, can be 'influxdb' or 'memory'.      | `memory`                        |
| `controller.databases.timeseries.dbfile`        | If using the 'memory' type, the path to the file where the time series data is stored as a CSV format.      | `/opt/premiscale/timeseries.db` |
| `controller.databases.timeseries.trailing`      | Seconds of collected time series data to keep and evaluate upon (must be >=interval). Default is 20 minutes | `1200`                          |

### Platform Configuration

| Name                                    | Description                                                                                                                 | Value                   |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| `controller.platform`                   | Configure the platform                                                                                                      | `{}`                    |
| `controller.platform.actionsQueueMax`   | The maximum number of inbound actions from the platform to queue up before dropping them. 0 means no limit.                 | `0`                     |
| `controller.platform.domain`            | The domain of the platform.                                                                                                 | `$PREMISCALE_PLATFORM`  |
| `controller.platform.token`             | The token to use to authenticate with the platform.                                                                         | `$PREMISCALE_TOKEN`     |
| `controller.platform.certificates`      | For local-only testing, you can provide self-signed certificates to the controller for connection to the platform services. | `{}`                    |
| `controller.platform.certificates.path` | Path to a directory containing the controller's certificates.                                                               | `/opt/premiscale/certs` |

### Reconciliation Configuration

| Name                                 | Description                                                                                                                                                                  | Value |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- |
| `controller.reconciliation.interval` | How often the controller reconciles the state of the ASGs. The controller collects time series and state in separate databases and queues up actions for autoscaling groups. | `60`  |

### Autoscaling Configuration

| Name                          | Description                                                  | Value |
| ----------------------------- | ------------------------------------------------------------ | ----- |
| `controller.autoscale.hosts`  | Groups of hosts to assign to ASGs.                           | `[]`  |
| `controller.autoscale.groups` | Specify and configure autoscaling groups on the hosts above. | `{}`  |

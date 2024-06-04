# `default.yaml`

## Parameters

### Controller Configuration

| Name                                                 | Description                                                                                                                 | Value                            |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `controller`                                         | Configure the controller, such as database connection criteria and how often to take certain controller-specific actions.   | `{}`                             |
| `controller.pidFile`                                 | Path to the file where the controller daemon process writes its PID.                                                        | `/opt/premiscale/premiscale.pid` |
| `controller.healthcheck`                             | Configure the healthcheck endpoint for the controller.                                                                      | `{}`                             |
| `controller.healthcheck.host`                        | The host to bind the healthcheck endpoint to.                                                                               | `127.0.0.1`                      |
| `controller.healthcheck.port`                        | The port to bind the healthcheck endpoint to.                                                                               | `8085`                           |
| `controller.healthcheck.path`                        | The path to bind the healthcheck endpoint to.                                                                               | `/healthz`                       |
| `controller.databases.state.type`                    | The type of database to use for storing state. Can be 'mysql' or 'sqlite' or 'memory'.                                      | `memory`                         |
| `controller.databases.state.collectionInterval`      | How often the agent collects metrics and stores them in the database.                                                       | `60`                             |
| `controller.databases.metrics.type`                  | The type of database to use for storing metrics. At this time, can be 'influxdb' or 'memory'.                               | `memory`                         |
| `controller.databases.metrics.collectionInterval`    | How often the agent retrieves metrics from all of the connected hosts.                                                      | `60`                             |
| `controller.databases.metrics.maxThreads`            | Establish connections to hosts in maxThreads-batches.                                                                       | `10`                             |
| `controller.databases.metrics.hostConnectionTimeout` | How long to wait for a connection to a host before timing out.                                                              | `60`                             |
| `controller.databases.metrics.trailing`              | Seconds of collected metrics to keep and evaluate upon (must be >=interval). Default is 20 minutes                          | `1200`                           |
| `controller.platform`                                | Configure the platform                                                                                                      | `{}`                             |
| `controller.platform.actionsQueueMax`                | The maximum number of actions from the platform to queue up before dropping them. 0 means no limit.                         | `0`                              |
| `controller.platform.domain`                         | The domain of the platform.                                                                                                 | `$PREMISCALE_PLATFORM`           |
| `controller.platform.token`                          | The token to use to authenticate with the platform.                                                                         | `$PREMISCALE_TOKEN`              |
| `controller.platform.certificates`                   | For local-only testing, you can provide self-signed certificates to the controller for connection to the platform services. | `{}`                             |
| `controller.platform.certificates.path`              | Path to a directory containing the controller's certificates.                                                               | `/opt/premiscale/certs`          |

### Reconciliation Configuration

| Name                                 | Description                                                                                                                                                                                    | Value |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- |
| `controller.reconciliation.interval` | How often the controller reconciles the state of the ASGs. The controller collects metrics and state in separate databases and queues up actions for autoscaling groups in separate processes. | `60`  |

### Autoscaling Configuration

| Name                          | Description                                                  | Value |
| ----------------------------- | ------------------------------------------------------------ | ----- |
| `autoscale.hosts`             | ] Groups of hosts to assign to ASGs.                         | `""`  |
| `controller.autoscale.groups` | Specify and configure autoscaling groups on the hosts above. | `{}`  |

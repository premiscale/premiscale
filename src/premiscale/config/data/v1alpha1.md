# PremiScale config version `v1alpha1`

This documentation outlines the `v1alpha1` configuration specification.

## Parameters

### Controller Configuration

| Name                                                           | Description                                                                                                                                                             | Value                   |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| `controller`                                                   | Configure the controller, such as database connection criteria and how often to take certain controller-specific actions.                                               | `{}`                    |
| `contoller.databases`                                          | Configure the databases the controller uses to store state and metrics.                                                                                                 | `{}`                    |
| `controller.databases.state`                                   | State is where the ASGs' current state as of the (latest reconciliation loop execution) is stored so it can be queried without making additional calls through libvirt. | `{}`                    |
| `controller.databases.state.collectionInterval`                | How often the agent collects metrics and stores them in the database.                                                                                                   | `60`                    |
| `controller.databases.state.type`                              | The type of database to use for storing state. Can be 'mysql' or 'sqlite' or 'memory'.                                                                                  | `mysql`                 |
| `controller.databases.state.connection`                        | Connection details for the state database.                                                                                                                              | `{}`                    |
| `controller.databases.state.connection.url`                    | The URL of the database.                                                                                                                                                | `$MYSQL_HOST`           |
| `controller.databases.state.connection.database`               | The name of the database to create or use, if it already exists.                                                                                                        | `premiscale`            |
| `controller.databases.state.connection.credentials`            | The credentials to use to connect to the database.                                                                                                                      | `{}`                    |
| `controller.databases.state.connection.credentials.username`   | The username to use to connect to the database.                                                                                                                         | `$MYSQL_USERNAME`       |
| `controller.databases.state.connection.credentials.password`   | The password to use to connect to the database.                                                                                                                         | `$MYSQL_PASSWORD`       |
| `controller.databases.metrics`                                 | How often metrics collection is performed from every host.                                                                                                              | `{}`                    |
| `controller.databases.metrics.collectionInterval`              | How often the agent retrieves metrics from all of the connected hosts.                                                                                                  | `60`                    |
| `controller.databases.metrics.maxThreads`                      | Establish connections to hosts in maxThreads-batches.                                                                                                                   | `10`                    |
| `controller.databases.metrics.hostConnectionTimeout`           | How long to wait for a connection to a host before timing out.                                                                                                          | `60`                    |
| `controller.databases.metrics.trailing`                        | Seconds of collected metrics to keep and evaluate upon (must be >=interval). Default is 20 minutes                                                                      | `1200`                  |
| `controller.databases.metrics.type`                            | The type of database to use for storing metrics. Can be 'influxdb' or 'memory'.                                                                                         | `influxdb`              |
| `controller.databases.metrics.connection`                      | Connection details for the metrics database.                                                                                                                            | `{}`                    |
| `controller.databases.metrics.connection.url`                  | The URL of the database.                                                                                                                                                | `$INFLUXDB_HOST`        |
| `controller.databases.metrics.connection.database`             | The name of the database to create or use.                                                                                                                              | `premiscale`            |
| `controller.databases.metrics.connection.credentials`          | The credentials to use to connect to the database.                                                                                                                      | `{}`                    |
| `controller.databases.metrics.connection.credentials.username` | The username to use to connect to the database.                                                                                                                         | `$INFLUXDB_USERNAME`    |
| `controller.databases.metrics.connection.credentials.password` | The password to use to connect to the database.                                                                                                                         | `$INFLUXDB_PASSWORD`    |
| `controller.platform`                                          | Configure the platform                                                                                                                                                  | `{}`                    |
| `controller.platform.actionsQueueMax`                          | The maximum number of actions to queue up FIFO before dropping them. 0 means no limit.                                                                                  | `0`                     |
| `controller.platform.domain`                                   | The domain of the platform.                                                                                                                                             | `$PREMISCALE_PLATFORM`  |
| `controller.platform.certificates`                             | For local-only testing, you can provide self-signed certificates to the controller for connection to the platform services.                                             | `{}`                    |
| `controller.platform.certificates.path`                        | Path to a directory containing the controller's certificates.                                                                                                           | `/opt/premiscale/certs` |

### Reconciliation Configuration


### Autoscaling Configuration

| Name                      | Description                                            | Value |
| ------------------------- | ------------------------------------------------------ | ----- |
| `autoscale`               | Configure hosts and autoscaling groups on those hosts. | `{}`  |
| `autoscale.hosts`         | Groups of hosts to assign to ASGs.                     | `{}`  |
| `autoscale.hosts.group-1` | An example group of hosts to assign to an ASG.         | `[]`  |




## Install PremiScale

Paraphrased, this should look like...

On your hosts, create a new user with XXX permissions and generate a new set of RSA keys for use with SSH (if that's your method of authentication with libvirt or the hosts, qemu+ssh:// e.g.) or, alternatively, we set up connectivity over TLS.

## Configuration File

The controller requires a user-provided config file in order to interact with hosts and virtual machines in your infrastructure. Please see the latest configuration file's [documentation](../../src/premiscale/config/data/README.md) and configure `controller.config` in the parameters below, accordingly.

## Parameters

### Global Configuration

| Name                       | Description                                                         | Value       |
| -------------------------- | ------------------------------------------------------------------- | ----------- |
| `global.image.registry`    | The global docker registry for all of the image.                    | `docker.io` |
| `global.image.pullSecrets` | ] Container registry pull secrets applied to every container image. | `""`        |

### Controller Deployment

| Name                                   | Description                                                                  | Value                   |
| -------------------------------------- | ---------------------------------------------------------------------------- | ----------------------- |
| `deployment.image.name`                | The name of the controller image.                                            | `premiscale/premiscale` |
| `deployment.image.tag`                 | The tag of the controller image.                                             | `0.0.1`                 |
| `deployment.image.pullPolicy`          | The pull policy of the controller image.                                     | `Always`                |
| `deployment.image.pullSecrets`         | ] Container registry pull secrets that only pertain to this container image. | `""`                    |
| `deployment.resources.requests.cpu`    | The CPU request for the controller container.                                | `0.5`                   |
| `deployment.resources.requests.memory` | The memory request for the controller container.                             | `1Gi`                   |
| `deployment.resources.limits.cpu`      | The CPU limit for the controller container.                                  | `4.0`                   |
| `deployment.resources.limits.memory`   | The memory limit for the controller container.                               | `2Gi`                   |
| `deployment.podSecurityContext`        | Configure the controller pod's security context.                             | `{}`                    |
| `deployment.containerSecurityContext`  | Configure the controller container's security context.                       | `{}`                    |
| `deployment.annotations`               | Annotations to be added to the deployment.                                   | `{}`                    |
| `deployment.labels`                    | Labels to be added to the deployment.                                        | `{}`                    |
| `deployment.startupProbe`              | Configure the deployment's startup probe.                                    | `{}`                    |
| `deployment.startupProbe.enabled`      | Enable or disable the startup probe.                                         | `false`                 |
| `deployment.startupProbe.path`         | The startup probe endpoint's path.                                           | `/health`               |
| `deployment.startupProbe.port`         | The startup probe endpoint's port.                                           | `8085`                  |
| `deployment.startupProbe.config`       | Additional configuration for the startup probe.                              | `{}`                    |
| `deployment.livenessProbe`             | Configure the deployment's liveness probe.                                   | `{}`                    |
| `deployment.livenessProbe.enabled`     | Enable or disable the liveness probe.                                        | `false`                 |
| `deployment.livenessProbe.path`        | The liveness probe endpoint's path.                                          | `/health`               |
| `deployment.livenessProbe.port`        | The liveness probe endpoint's port.                                          | `8085`                  |
| `deployment.livenessProbe.config`      | Additional configuration for the liveness probe.                             | `{}`                    |
| `deployment.readinessProbe`            | Configure the deployment's readiness probe.                                  | `{}`                    |
| `deployment.readinessProbe.enabled`    | Enable or disable the readiness probe.                                       | `false`                 |
| `deployment.readinessProbe.path`       | The readiness probe endpoint's path.                                         | `/ready`                |
| `deployment.readinessProbe.port`       | The readiness probe endpoint's port.                                         | `8085`                  |
| `deployment.readinessProbe.config`     | Additional configuration for the readiness probe.                            | `{}`                    |
| `deployment.extraEnv`                  | ] Extra environment variables to be passed to the controller container.      | `""`                    |
| `deployment.extraPorts`                | ] Extra ports to be exposed on the controller container.                     | `""`                    |

### PremiScale Controller

| Name                                    | Description                                                                                                                                                                                                          | Value                           |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| `controller.registration.createSecret`  | If true, the controller will create a secret with the registration token. If false, the secret must already exist.                                                                                                   | `false`                         |
| `controller.registration.secretName`    | The name of the secret that contains the registration token. If createSecret is true, the controller will create this secret. If createSecret is false, the controller will use this secret and expects it to exist. | `premiscale-registration-token` |
| `controller.registration.key`           | The key in the secret that contains the registration token.                                                                                                                                                          | `token`                         |
| `controller.registration.value`         | User-provided platform registration key.                                                                                                                                                                             | `""`                            |
| `controller.registration.immutable`     | If true, the registration secret cannot be updated. If false, the registration secret can be updated.                                                                                                                | `true`                          |
| `controller.config.mountPath`           | The path where the controller config file is mounted.                                                                                                                                                                | `/opt/premiscale/config.yaml`   |
| `controller.logging.level`              | Can be one of info|debug|warn|error.                                                                                                                                                                                 | `info`                          |
| `controller.extraEnv`                   | ] Extra environment variables to be passed to the controller container. These are useful for injecting and referencing environment variables in the config that's read from the ConfigMap below.                     | `""`                            |
| `controller.libvirt`                    | Configuration for the libvirt provider.                                                                                                                                                                              | `{}`                            |
| `controller.platform.domain`            | The domain of the platform.                                                                                                                                                                                          | `$PREMISCALE_PLATFORM`          |
| `controller.platform.certificates`      | For local-only testing, you can provide self-signed certificates to the controller for connection to the platform services.                                                                                          | `{}`                            |
| `controller.platform.certificates.path` | If using a self-signed certificate for development purposes, specify the path.                                                                                                                                       | `''`                            |

### RBAC configuration

| Name                    | Description                                 | Value   |
| ----------------------- | ------------------------------------------- | ------- |
| `serviceAccount.create` | If true, a service account will be created. | `false` |

### PremiScale Controller Config

| Name                    | Description                                                                                                    | Value   |
| ----------------------- | -------------------------------------------------------------------------------------------------------------- | ------- |
| `configMap.enabled`     | Enable or disable the ConfigMap. If enabled, the controller will read its config from the specified ConfigMap. | `false` |
| `configMap.config`      | The controller config file.                                                                                    | `""`    |
| `configMap.immutable`   | If true, the ConfigMap cannot be updated. If false, the ConfigMap can be updated.                              | `false` |
| `configMap.labels`      | Labels to be added to the ConfigMap.                                                                           | `{}`    |
| `configMap.annotations` | Annotations to be added to the ConfigMap.                                                                      | `{}`    |

### Controller service

| Name                     | Description                                                                                                                            | Value       |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `service.enabled`        | Enable or disable the service. If ingress is enabled, the service type is automatically enabled and the type switched to LoadBalancer. | `true`      |
| `service.type`           | The service type.                                                                                                                      | `ClusterIP` |
| `service.ports.liveness` | Configure the liveness probe port.                                                                                                     | `{}`        |

### Kubernetes autoscaler

| Name                         | Description                                                                                                                                                       | Value   |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| `cluster-autoscaler.enabled` | Enable or disable the autoscaler dependency of the PremiScale controller. Enable this if you would like to autoscale the cluster on which the controller resides. | `false` |

## Install PremiScale



## Parameters

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
| `deployment.livenessProbe`             | Configure the deployment's liveness probe.                                   | `{}`                    |
| `deployment.readinessProbe`            | Configure the deployment's readiness probe.                                  | `{}`                    |
| `deployment.ports`                     | The ports that the controller container exposes.                             | `[]`                    |

### PremiScale Controller

| Name                                   | Description                                                                                                                                                                                                          | Value                           |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| `controller.registration.createSecret` | If true, the controller will create a secret with the registration token. If false, the secret must already exist.                                                                                                   | `false`                         |
| `controller.registration.secretName`   | The name of the secret that contains the registration token. If createSecret is true, the controller will create this secret. If createSecret is false, the controller will use this secret and expects it to exist. | `premiscale-registration-token` |
| `controller.registration.key`          | The key in the secret that contains the registration token.                                                                                                                                                          | `token`                         |
| `controller.registration.value`        | User-provided platform registration key.                                                                                                                                                                             | `""`                            |
| `controller.registration.immutable`    | If true, the registration secret cannot be updated. If false, the registration secret can be updated.                                                                                                                | `true`                          |
| `controller.config.mountPath`          | The path where the controller config file is mounted.                                                                                                                                                                | `/opt/premiscale/config.yaml`   |
| `controller.logging.level`             | Can be one of info|debug|warn|error.                                                                                                                                                                                 | `info`                          |
| `controller.extraEnv`                  | ] Extra environment variables to be passed to the controller container. These are useful for injecting and referencing environment variables in the config that's read from the ConfigMap below.                     | `""`                            |

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

| Name                                           | Description                                                                                                                                                       | Value                           |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| `cluster-autoscaler.enabled`                   | Enable or disable the autoscaler dependency of the PremiScale controller. Enable this if you would like to autoscale the cluster on which the controller resides. | `false`                         |
| `cluster-autoscaler.image.repository`          | The repository of the autoscaler image.                                                                                                                           | `kubernetes/cluster-autoscaler` |
| `cluster-autoscaler.image.tag`                 | The tag of the autoscaler image.                                                                                                                                  | `v1.28.2`                       |
| `cluster-autoscaler.image.pullPolicy`          | The pull policy of the autoscaler image.                                                                                                                          | `IfNotPresent`                  |
| `cluster-autoscaler.resources.limits.cpu`      | The CPU limit for the autoscaler container.                                                                                                                       | `100m`                          |
| `cluster-autoscaler.resources.limits.memory`   | The memory limit for the autoscaler container.                                                                                                                    | `300Mi`                         |
| `cluster-autoscaler.resources.requests.cpu`    | The CPU request for the autoscaler container.                                                                                                                     | `100m`                          |
| `cluster-autoscaler.resources.requests.memory` | The memory request for the autoscaler container.                                                                                                                  | `300Mi`                         |

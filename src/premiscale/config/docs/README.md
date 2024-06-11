# PremiScale controller configuration

Local controller config versions are documented here. When a controller with no user-provided config starts for the first time, a default config is created, which always reflects the latest version available as of the release.

- [`default`](./default.md): the [default.yaml](./../default.yaml) that's created when no user-provided config is found.
- [`v1alpha1`](./v1alpha1.md)

## Validating configuration files

Validate a config file with the following command.

```shell
premiscale --config src/premiscale/config/default.yaml --validate --log-stdout
```
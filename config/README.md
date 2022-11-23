# Configuration overview

I'm still planning out the schema of the config file below, but this is my first-pass design for a release.

```yaml
version: v1
scaling:
    databases:
    # State is where the ASGs current state is stored so it can be queried without making additional calls to libvirt.
    state:
        store:
        type: mysql
        connection:
            url: localhost
            port: 3306
            credentials:
            env:
                username: $MYSQL_USERNAME
                password: $MYSQL_PASSWORD

    metrics:
        # Define where to store metrics: either in-memory or influxdb, since that's a time-series db I'm familiar with for now.
        store:
        type: local

        # store:
        #   type: influxdb
        #   url: http://localhost:8086/
        #   credentials:
        #     env:
        #       username: $INFLUXDB_USERNAME
        #       password: $INFLUXDB_PASSWORD

        # Seconds, minutes or hours between collecting metrics from all hosts on their VMs.
        interval: 30s

        # How often to evaluate all 'trailing' metrics.
        evaluate: 1m

        # Seconds, minutes or hours of collected metrics to cache and evaluate upon (must be >=interval)
        trailing: 21m

    hostGroups:
    group-1:
        # All hosts in group-1 should be pretty similar. Hosts differing by any great amount should be
        # managed as a separate group? But they should all be within reach of an ~/.ssh/config.
        - name: localhost
        address: qemu+ssh:///system
        - name: domain-1
        address: qemu+ssh://domain-1/system
        - name: domain-2
        address: qemu+ssh://domain-2/system

    autoscalingGroups:
    # Unique keys defining separate VM groups to track. These keys should represent naming prefixes (?)
    rivendell:
        # This image and an associated libvirt template should exist on one of the hosts.
        image:
        name: template-ubuntu20.04-server
        # Options could be 'migrate' - migrate a copy of the domain to every host, or 'centralized' - hosts are using a centralized block store.
        imageMigration: migrate
        # Whether or not to delete the former image on all hosts but one.
        retention:
            strategy: delete
            keep:
        cloud-init:
        inline: |
            # Should contain an inline cloud-init script by which to customize VMs in this group, or you can specify a "file: "-keyword to read it from some location on-disk. All environment variables should be evaluated and replaced before bundling with the domains' disks?

        # file:

        # Group of hosts on which to provision VMs.
        hostGroup: group-1

        replacement:
        strategy: rollingupdate
        # replace one VM at a time if there's an image update in a group in this file, etc.
        maxUnavailable: 1

        networking:
        # A static IP range or list of IPs should be given to a group.
        addresses:
            - 192.168.5.2-192.168.5.254
        subnet: 255.255.255.0
        gateway: 192.168.1.1

        scaling:
        # maxNodes should not be larger than the number of IP addresses determined to be available in the range.
        maxNodes: 10
        minNodes: 3
        # Increment up or down by this many nodes any time a change is required to state.
        increment: 1
        # Seconds, minutes or hours until another action can be taken once a change is made. Basically puts a pause on metrics evaluation.
        cooldown: 5m

        metrics:
            # I need to work out how to determine percentages and such here. Disk IO isn't as straightforward. CPU could be based on VM load average? And memory could be based more-easily on a percentage.
            io: 80
            cpu: 80
            memory: 80
    mordor:
        ...

```

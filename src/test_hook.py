#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shorthand to testing code.
"""


import logging

from ipaddress import IPv4Address
from premiscale.metrics.state.local import Local
from premiscale.config._v1alpha1 import Host


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def test_local_state():
    with Local() as state:
        assert state.is_connected()

        state.reset()

        print(
            state.run(
                'SELECT * FROM sqlite_master;'
            )
        )

        print(
            state.host_report()
        )

        print(
            state.host_create(
                'localhost',
                '127.0.0.1',
                'SSH',
                11111,
                'kvm',
                4,
                103079215104,
                8589934592
            )
        )

        print(
            state.host_report()
        )

    # assert not state.is_connected()


def test_qemu_hypervisor():
    from premiscale.hypervisor import build_hypervisor_connection

    with build_hypervisor_connection(
            Host(
                hypervisor='qemu',
                name='rocinante',
                user='emma',
                address=IPv4Address('10.0.0.100'),
                port=22,
                protocol='SSH'
            )
        ) as hypervisor:
        pass


if __name__ == '__main__':
    test_local_state()
    test_qemu_hypervisor()
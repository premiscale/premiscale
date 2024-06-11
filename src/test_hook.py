#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shorthand to testing code.
"""


from functools import partial
from premiscale.metrics.state.local import Local


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

    assert not state.is_connected()


if __name__ == '__main__':
    test_local_state()
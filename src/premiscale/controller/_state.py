"""
A high-level interface to working with different state backends.
"""


from cattrs import unstructure
from premiscale.config.v1alpha1 import Config
from premiscale.state._base import State


def build_state(config: Config) -> State:
    """
    Manufacture a state backend based on the configuration.
    """
    match config.controller.databases.state.type:
        case 'memory':
            # SQLite
            from premiscale.state.local import Local

            return Local()
        case 'mysql':
            from premiscale.state.mysql import MySQL

            connection = unstructure(config.controller.databases.state.connection)
            del(connection['type'])

            return MySQL(**connection)
        case _:
            raise ValueError(f'Unknown state type: {config.controller.databases.state.type}')
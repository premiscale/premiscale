"""
Encapsulates the API for the PremiScale controller.
"""


from flask import cli


# TODO: Remove this hack and build out a system of creating APIs for the controller.
cli.show_server_banner = lambda *x: None
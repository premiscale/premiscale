"""
Primary autoscaler interface.
"""


from argparse import ArgumentParser, RawDescriptionHelpFormatter


def cli() -> None:
    """
    Set up the CLI for autoscaler.
    """
    parser = ArgumentParser()

    args = parser.parse_args()


if __name__ == '__main__':
    cli()

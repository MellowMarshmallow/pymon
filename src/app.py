#!/usr/bin/env python


"""
cli for pymon
"""


import logging
import pymon.gen.char
import pymon.log


def _dev() -> None:
    """for testing purposes"""

    # configure logging system
    level = logging.DEBUG
    handler = pymon.log.create_cli_handler(level)
    pymon.log.configure_logger(level, handler)

    # pymon.setup.download_data()
    pymon.gen.char.main()


if __name__ == "__main__":
    _dev()

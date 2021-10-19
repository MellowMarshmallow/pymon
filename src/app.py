#!/usr/bin/env python


"""
cli for paimon
"""


import logging
import pymon.log
import pymon.setup


def __run_tests__() -> None:
    """for testing purposes"""

    # configure logging system
    level = logging.INFO
    handler = pymon.log.create_cli_handler(level)
    pymon.log.configure_logger(level, handler)

    # pymon.setup.download_data()


if __name__ == "__main__":
    __run_tests__()

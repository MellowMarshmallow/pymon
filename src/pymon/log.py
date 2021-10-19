#!/usr/bin/env python


"""
Implements basic logging features.
"""


import logging
import colorlog


def get_logger(name=__name__) -> logging.Logger:
    return logging.getLogger(name)


def configure_logger(
    level: "logging._Level", *handlers: logging.Handler, name=__name__
) -> None:
    logger = logging.getLogger(name)

    logger.setLevel(level)
    for handler in handlers:
        logger.addHandler(handler)


def create_cli_handler(level: "logging._Level") -> logging.StreamHandler:
    attributes = (
        "%(levelname)-8s",
        "%(module)-10s",
        "%(funcName)-20s",
        "%(lineno)-4d",
        "%(message)s",
    )
    delimiter = " | "

    formatter = colorlog.ColoredFormatter(
        delimiter.join(
            [f"%(log_color)s{attribute}%(reset)s" for attribute in attributes]
        )
    )

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)

    return handler


if __name__ == "__main__":
    cli = create_cli_handler(logging.DEBUG)
    configure_logger(logging.DEBUG, cli)
    test_logger = get_logger()

    test_logger.debug("For the purpose of debugging")
    test_logger.info("General information")
    test_logger.warning("Uh oh")
    test_logger.error("Well this is a problem")
    test_logger.critical("Everything is on fire")

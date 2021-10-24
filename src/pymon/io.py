#!/usr/bin/env python


"""
For reading and writing data.
"""


from typing import Any
from pathlib import Path
import json
import pymon.log


logger = pymon.log.get_logger()


def read(path: str) -> Any:
    """Implements how to read data files."""

    try:
        logger.info("Read %s", path)

        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        logger.info("Read %s ... done", path)
        return data
    except FileNotFoundError:
        logger.critical("Read %s ... failed", path)
        raise


def write(path: str, serializable_data: Any) -> None:
    """Implements how to write data files."""

    try:
        logger.info("Write data to %s", path)
        logger.debug("data == %s", serializable_data)

        with open(path, "w", encoding="utf-8") as file:
            json.dump(serializable_data, file, indent=4, sort_keys=True)

        logger.info("Write data to %s ... done", path)
    except FileNotFoundError:
        logger.critical("Unable to open %s", path)
        raise
    except TypeError:
        logger.critical("Data is not serializable")
        raise


def file_name(path: str) -> str:
    """Returns the filename (without file extension)."""

    return Path(path).stem

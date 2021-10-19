#!/usr/bin/env python


"""
for setting up the application
"""


import subprocess
import pymon.log


logger = pymon.log.get_logger()


def download_data() -> None:
    """Download data files from Dimbreath/GenshinData"""

    command = "./script/pull-data.sh"
    logger.info("Running %s", command)

    try:
        # TODO: live logging of process output
        result = subprocess.run([command], capture_output=True, text=True, check=True)
        for line in filter(None, result.stdout.split("\n")):
            logger.info("%s", line)
    except FileNotFoundError:
        logger.critical("%s does not exist", command)
    except subprocess.CalledProcessError as error:
        logger.critical("%s returned %d", command, error.returncode)

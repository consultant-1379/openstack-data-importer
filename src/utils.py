"""This module contains common utility functions used by other modules."""

import logging
import subprocess
import shlex

LOG = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


class CliNonZeroExitCodeException(Exception):
    """
    Custom exception for expressing non zero exit codes.

    This custom exception is used to convey when a cli command
    has executed and returned a non zero exit code
    """

    pass


def run_cli_command(command):
    """
    Run the given cli command and return the result.

    Args:
        command (str): The first parameter

    Returns:
        dictionary containing two keys,
        the standard_error, and standard_output strings

    Raises:
        Exception: if the return code is not 0

    """
    LOG.info("Running cli command (" + command + ")")
    process = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process_standard_output, process_standard_error = process.communicate()
    if process.returncode != 0:
        raise CliNonZeroExitCodeException(
            'The command failed with exit code ' + str(process.returncode) +
            '. Heres the output: ' + process_standard_output +
            '\nError: ' + process_standard_error
        )
    LOG.debug(process_standard_output)
    LOG.debug(process_standard_error)
    LOG.info("cli command completed")
    return {
        'standard_output': process_standard_output,
        'standard_error': process_standard_error
    }

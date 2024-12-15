import typing as t
import subprocess

from kvcommon.logger import get_logger

logger = get_logger("KVC")


def shell_cmd(cmd: str, raise_exceptions: bool = False) -> str:
    try:
        command_line_process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        stdout, stderr = command_line_process.communicate()

        if stderr:
            logger.error(stderr)

        if isinstance(stdout, str):
            return stdout
        return stdout.decode("utf-8")

    except (OSError, subprocess.CalledProcessError) as ex:
        logger.error("Exception occured: " + str(ex))
        if raise_exceptions:
            raise ex
        return str(ex)

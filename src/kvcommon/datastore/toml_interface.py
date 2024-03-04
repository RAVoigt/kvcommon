from __future__ import annotations
import os
import pathlib
import toml
import typing as t

from kvcommon import logger

LOG = logger.get_logger("iaptoolkit-datastore")


class TOMLInterface(object):
    """
    Simple interface for writing and reading TOML files to/from dict
    """

    def __init__(
        self,
        storage_dir_path: str | pathlib.Path,
        user_conf_filename: str | pathlib.Path,
    ) -> None:
        # Separate vars for dir and file to ease creation of dir if it doesn't exist
        self.USER_DIR = pathlib.Path(storage_dir_path)
        self.USER_CONF_PATH = self.USER_DIR / user_conf_filename

    def write_data(self, data: dict):
        """Writes a config dict as a .toml file to the path from constants.

        Also ensure that permissions are appropriate for a file that we're storing
        tokens and secrets in.
        """
        try:
            # TODO: Better error handling
            self.USER_DIR.mkdir(exist_ok=True, parents=True)
            self.USER_CONF_PATH.touch(exist_ok=True)

            # Ensure permissions are good before we store anything
            os.chmod(self.USER_DIR, 0o700)
            os.chmod(self.USER_CONF_PATH, 0o700)

            with open(self.USER_CONF_PATH, "w") as toml_file:
                toml.dump(data, toml_file)
        except OSError as ex:
            LOG.error(
                f"Failed to write config to TOML at path: {self.USER_CONF_PATH}, "
                "full_exception={ex}"
            )
            raise ex

    def read_data(self) -> t.Dict:
        """Load the config .toml file from its path in the user dir.

        Returns the user config as a dict. If the file doesn't already exist,
        a fresh config file is created and its contents returned.
        """
        data = dict()
        if not self.USER_CONF_PATH.is_file():
            data["tokens"] = dict(refresh=None)
            self.write_data(data)

        else:
            try:
                data: dict = toml.load(self.USER_CONF_PATH)
            except OSError as ex:
                LOG.error(
                    f"Failed to load config from TOML at path: {self.USER_CONF_PATH}, "
                    "full_exception={ex}"
                )
                raise ex

        return data

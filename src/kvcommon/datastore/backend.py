from __future__ import annotations
from abc import ABC
from abc import abstractmethod
import os
import pathlib
import typing as t

import toml

from kvcommon import logger


LOG = logger.get_logger("kvc-ds")


class DatastoreBackend(ABC):
    @property
    @abstractmethod
    def _data_by_ref(self) -> dict:
        """
        Return a reference to a dict containing this backend's data
        """
        raise NotImplementedError()

    @property
    def _data(self) -> dict:
        """
        Return a copy of the the dict containing this backend's data
        """
        return self._data_by_ref.copy()

    def get(self, key, default=None, by_ref: bool = False):
        """
        Get a key:value pair in the backend.
        Access the backend's data by-reference (skipping the dict.copy() call) if by_ref is True.
        """
        if by_ref:
            return self._data_by_ref.get(key, default)
        return self._data.get(key, default)

    @abstractmethod
    def set(self, key, value) -> None:
        """
        Set a key:value pair in the backend
        """
        raise NotImplementedError()

    @abstractmethod
    def overwrite_data(self, data: dict) -> None:
        """
        Overwrite the entire contents of the backend's data with a new dict
        """
        raise NotImplementedError()

    def update_data(self, **overrides: dict) -> None:
        """
        Update the backend's data dict with the contents of the overrides dict
        """
        data = self._data_by_ref
        data.update(overrides)
        self.overwrite_data(data)


class DictBackend(DatastoreBackend):
    _data_dict: dict

    def __init__(self) -> None:
        self._data_dict = dict()

    @property
    def _data_by_ref(self) -> dict:
        return self._data_dict

    def set(self, key, value):
        self._data_dict[key] = value

    def overwrite_data(self, data: dict) -> None:
        self._data_dict = data


class TOMLBackend(DatastoreBackend):
    def __init__(
        self,
        storage_dir_path: str | pathlib.Path,
        filename: str | pathlib.Path,
    ) -> None:
        self.BASE_DIR = pathlib.Path(storage_dir_path)
        if str(self.BASE_DIR).startswith("~"):
            self.BASE_DIR = self.BASE_DIR.expanduser()
        self.BASE_FILE_PATH = self.BASE_DIR / filename
        if not str(self.BASE_FILE_PATH).endswith(".toml"):
            self.BASE_FILE_PATH = self.BASE_FILE_PATH.with_suffix(".toml")

    @property
    def _data_by_ref(self) -> dict:
        return self.read_data()

    def set(self, key, value):
        self.update_data(**{key: value})

    def overwrite_data(self, data: dict) -> None:
        self.write_data(data)

    def write_data(self, data: dict):
        """Writes a config dict as a .toml file to the path from constants.

        Also ensure that permissions are appropriate for a file that we're storing
        tokens and secrets in.
        """
        try:
            # TODO: Better error handling
            self.BASE_DIR.mkdir(exist_ok=True, parents=True)
            self.BASE_FILE_PATH.touch(exist_ok=True)

            # Ensure permissions are good before we store anything
            os.chmod(self.BASE_DIR, 0o700)
            os.chmod(self.BASE_FILE_PATH, 0o700)

            with open(self.BASE_FILE_PATH, "w") as toml_file:
                toml.dump(data, toml_file)
        except OSError as ex:
            LOG.error(
                "Failed to write config to TOML at path: '%s' - full_exception=%s",
                self.BASE_FILE_PATH,
                ex,
            )
            raise ex

    def read_data(self) -> dict:
        """Load the config .toml file from its path in the user dir.

        Returns the user config as a dict. If the file doesn't already exist,
        a fresh config file is created and its contents returned.
        """
        data = dict()
        if not self.BASE_FILE_PATH.is_file():
            self.write_data(data)

        else:
            try:
                data: dict = toml.load(self.BASE_FILE_PATH)
            except OSError as ex:
                LOG.error(
                    "Failed to load config from TOML at path: '%s' - full_exception=%s",
                    self.BASE_FILE_PATH,
                    ex,
                )
                raise ex

        return data


# TODO
class YAMLBackend(DatastoreBackend):
    def __init__(self) -> None:
        raise NotImplementedError()
        super().__init__()

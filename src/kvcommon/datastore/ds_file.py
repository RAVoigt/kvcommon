from __future__ import annotations
import typing as t
import os
import pathlib
from abc import ABCMeta
from abc import abstractmethod

from kvcommon import logger
from kvcommon.types import PathLike

from .base import Datastore
from .ds_external import BulkOnlyExternalBackend


LOG = logger.get_logger("kvc-ds")


class FileBackend(BulkOnlyExternalBackend, metaclass=ABCMeta):
    """
    Abstract base class for file-backed datastores that maintain an in-memory dict but also sync
    to/from a file in a given serialization format (implemented by subclass)
    """

    _file_extension: str
    _storage_dir_path: PathLike
    _filename: PathLike

    def __init__(self, storage_dir_path: PathLike, filename: PathLike, write_on_update: bool = True) -> None:

        if not hasattr(self, "_file_extension"):
            raise NotImplementedError("Must initialize _file_extension str attr on any subclass of FileBackend")
        super().__init__(write_on_update=write_on_update)

        self.BASE_DIR = pathlib.Path(storage_dir_path)
        if str(self.BASE_DIR).startswith("~"):
            self.BASE_DIR = self.BASE_DIR.expanduser()

        self.BASE_FILE_PATH = self.BASE_DIR / filename
        if not str(self.BASE_FILE_PATH).endswith(self.file_extension):
            self.BASE_FILE_PATH = self.BASE_FILE_PATH.with_suffix(self.file_extension)

    @property
    def file_extension(self) -> str:
        if not hasattr(self, "_file_extension"):
            raise NotImplementedError("Must initialize _file_extension str attr on any subclass of FileBackend")
        return self._file_extension

    def _ensure_file_path(self):
        # TODO: Better error handling
        try:
            self.BASE_DIR.mkdir(exist_ok=True, parents=True)
            self.BASE_FILE_PATH.touch(exist_ok=True)

        except OSError as ex:
            LOG.error(
                "Failed to ensure file path: '%s' - full_exception=%s",
                self.BASE_FILE_PATH,
                ex,
            )
            raise ex

    def set_file_permissions(
        self, file_permissions_octal: int = 0o700, parent_dir_permissions_octal: int | None = None
    ):
        # TODO: Better error handling

        if parent_dir_permissions_octal is not None:
            try:
                os.chmod(self.BASE_DIR, parent_dir_permissions_octal)
            except OSError as ex:
                LOG.error(
                    "Failed to set parent dir permissions path: '%s' - full_exception=%s", self.BASE_FILE_PATH, ex
                )
                raise ex
        try:
            os.chmod(self.BASE_FILE_PATH, file_permissions_octal)
        except OSError as ex:
            LOG.error("Failed to set file path: '%s' - full_exception=%s", self.BASE_FILE_PATH, ex)
            raise ex

    @abstractmethod
    def serialize(self) -> str:
        """
        This method should implement serialization of this object's _data_dict to a string
        """
        raise NotImplementedError()

    @abstractmethod
    def deserialize(self, input: str) -> dict:
        """
        This method should implement deserialization of a string to a dict for this object's format
        """
        raise NotImplementedError()


    def write_data(self):
        """Writes dict data to a file."""
        self._ensure_file_path()
        try:
            with open(self.BASE_FILE_PATH, "w") as file:
                file.write(self.serialize())

        except OSError as ex:
            LOG.error(
                "Failed to write to file at path: '%s' - full_exception=%s",
                self.BASE_FILE_PATH,
                ex,
            )
            raise ex

    def read_data(self) -> dict:
        """
        Load the .toml file from its path in the user dir.
        If the file doesn't already exist, a fresh file is initialized and its contents returned.
        """
        data: t.Dict
        if not self.BASE_FILE_PATH.is_file():
            data = dict()
            self.overwrite_data(data)
            self.write_data()
        else:
            try:
                with open(self.BASE_FILE_PATH, "r") as file:
                    file_contents = file.read()
                    data = self.deserialize(file_contents)
            except OSError as ex:
                LOG.error(
                    "Failed to read from file at path: '%s' - full_exception=%s",
                    self.BASE_FILE_PATH,
                    ex,
                )
                raise ex
            self.overwrite_data(data)

        return data


class FileDatastore(Datastore):
    _backend_cls: t.Type[FileBackend]
    _backend: FileBackend

    def __init__(self, config_version: int, backend: FileBackend) -> None:
        super().__init__(config_version, backend)


def create_file_datastore(
    backend_cls: t.Type[FileBackend],
    config_version: int,
    storage_dir_path: PathLike,
    filename: PathLike,
    write_on_update: bool = True,
) -> FileDatastore:
    if backend_cls == FileBackend:
        raise ValueError("create_file_datastore() requires a concrete subclass of FileBackend")
    return FileDatastore(
        config_version,
        backend=backend_cls(
            storage_dir_path=storage_dir_path,
            filename=filename,
            write_on_update=write_on_update,
        ),
    )

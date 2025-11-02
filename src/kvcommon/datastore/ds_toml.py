from __future__ import annotations
import typing as t

import toml
from toml import TomlDecoder
from toml import TomlEncoder

from kvcommon import logger
from kvcommon.types import PathLike

from .ds_file import create_file_datastore
from .ds_file import FileBackend
from .ds_file import FileDatastore


LOG = logger.get_logger("kvc-ds-toml")


class TOMLBackend(FileBackend):
    _file_extension: str = ".toml"

    def serialize(self, encoder: TomlEncoder | None = None) -> str:
        return toml.dumps(o=self._data_dict, encoder=encoder)

    def deserialize(self, file_contents, decoder: TomlDecoder | None = None) -> dict:
        return toml.loads(s=file_contents, decoder=decoder)


def create_toml_datastore(
    config_version: int,
    storage_dir_path: PathLike,
    filename: PathLike,
    write_on_update: bool = True,
) -> FileDatastore:
    return create_file_datastore(TOMLBackend, config_version, storage_dir_path, filename, write_on_update)

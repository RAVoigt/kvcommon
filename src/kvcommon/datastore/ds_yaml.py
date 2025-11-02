from __future__ import annotations
import typing as t
import yaml

try:
    from ruamel.yaml import YAML  # pyright: ignore[reportMissingImports]

    RUAMEL_YAML_AVAILABLE = True
except ImportError:
    RUAMEL_YAML_AVAILABLE = False

from kvcommon import logger
from kvcommon.types import PathLike

from .ds_file import create_file_datastore
from .ds_file import FileBackend
from .ds_file import FileDatastore


LOG = logger.get_logger("kvc-ds")


class YAMLUtils:
    """
    A stupid wrapper to use pyyaml if ruamel.yaml is not available
    """

    @staticmethod
    def _get_ruamel_yaml() -> t.Any | None:
        if not RUAMEL_YAML_AVAILABLE:
            return None
        yaml = YAML()
        yaml.preserve_quotes = True
        return yaml

    @staticmethod
    def yaml_load(file_contents) -> dict:
        if not RUAMEL_YAML_AVAILABLE:
            return yaml.safe_load(file_contents)
        return YAMLUtils._get_ruamel_yaml.load(file_contents)

    @staticmethod
    def yaml_dump(data: dict) -> str:
        if not RUAMEL_YAML_AVAILABLE:
            return yaml.safe_dump(data, sort_keys=False, default_flow_style=False)
        return YAMLUtils._get_ruamel_yaml.dump(data)


class YAMLBackend(FileBackend):
    _file_extension: str = ".yaml"

    def serialize(self) -> str:
        return YAMLUtils.yaml_dump(self._data_dict)

    def deserialize(self, file_contents) -> dict:
        return YAMLUtils.yaml_load(file_contents)


class YAMLDatastore(FileDatastore):
    _backend_cls = YAMLBackend
    _backend: YAMLBackend


def create_yaml_datastore(
    config_version: int,
    storage_dir_path: PathLike,
    filename: PathLike,
    write_on_update: bool = True,
) -> FileDatastore:
    return create_file_datastore(YAMLBackend, config_version, storage_dir_path, filename, write_on_update)

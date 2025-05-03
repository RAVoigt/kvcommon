import typing as t
from .base import VersionedDatastore
from .backend import DictBackend


class InMemoryDatastore(VersionedDatastore):
    _backend: DictBackend

    def __init__(self, config_version: int) -> None:
        super().__init__(DictBackend(), config_version)


__all__ = [
    "VersionedDatastore",
    "InMemoryDatastore",
]

from __future__ import annotations
import typing as t

from kvcommon import logger

from .backend import DatastoreBackend


LOG = logger.get_logger("kvc-ds")


class VersionedDatastore(object):
    """
    Versioned Datastore

    An over-engineered wrapper around dict storage with rudimentary versioning.
    """

    _config_version: int
    _version_key = "_data_version"
    _backend: DatastoreBackend

    def __init__(
        self, backend: DatastoreBackend | t.Type[DatastoreBackend], config_version: int
    ) -> None:
        self._config_version = config_version
        if isinstance(backend, DatastoreBackend):
            self._backend = backend
        elif isinstance(backend, type(DatastoreBackend)):
            self._backend = backend()

        if not self.check_version_match():
            self._migrate_version()

    def check_version_match(self) -> bool:
        return self.get_data_version(allow_none=True) == self._config_version

    def _migrate_version(self):
        # LOG.debug("New config version detected. Migrating.")
        # ...
        # Subclasses should super() call this method after migrating data
        # ...
        self._set_data_version(self._config_version)

    def _set_data_version(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Attempting to set non-int value for config_version: {value}")
        self.set_value(self._version_key, value)

    def get_data_version(self, allow_none=True) -> int:
        value = self.get_value(self._version_key)
        if allow_none and value is None:
            return 0
        if not isinstance(value, int):
            raise TypeError(f"Non-int value retrieved for config_version: {value}")
        return value

    def get_value(self, key, default=None, by_ref=False) -> t.Any:
        return self._backend.get(key, default=default, by_ref=by_ref)

    def set_value(self, key, value):
        return self._backend.set(key, value)

    def get_or_create_nested_dict(self, key) -> dict:
        existing = self.get_value(key, default=None)
        if existing is None:
            existing = {}
            self.set_value(key, existing)
        elif not isinstance(existing, dict):
            raise TypeError(f"Non-dict value retrieved for key: {key}")
        return existing

    def overwrite_data(self, new_data: dict) -> None:
        return self._backend.overwrite_data(new_data)

    def update_data(self, **overrides: dict) -> None:
        return self._backend.update_data(**overrides)


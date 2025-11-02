from __future__ import annotations
import asyncio
import typing as t
from abc import ABCMeta
from abc import abstractmethod

from kvcommon import logger
from kvcommon.asynchronous.utils import call_sync_async
from kvcommon.asynchronous.utils import LoopType

from .backend import DatastoreBackend


LOG = logger.get_logger("kvc-ds")


class ExternalBackend(DatastoreBackend, metaclass=ABCMeta):
    """
    Abstract base class for externally-backed datastores that maintain an in-memory dict but also sync
    to/from an external destination such as a file, DB or network destination
    """

    _write_on_update_default: bool = True

    # If True, reads and writes to/from external destination are done across all key-value pairs,
    # not one-by-one
    # i.e.; if the backend destination is a file that must be updated all at once, rather than a
    # destination that supports writing individual key-value pairs.
    _full_sync_only: bool = False

    def __init__(self, write_on_update: bool = True) -> None:
        super().__init__()
        self._write_on_update_default = write_on_update

    def _update_external_on_change(self, key: t.Any | None = None, value: t.Any | None = None):
        if self._full_sync_only == False and key is not None and value is not None:
            return self.write_datum(key=key, value=value)
        return self.write_data()

    async def _update_external_on_change_async(
        self,
        key: t.Any | None = None,
        value: t.Any | None = None,
        loop: LoopType | None = None,
    ):
        if (not self._full_sync_only) and key is not None and value is not None:
            return await self.write_datum_async(key=key, value=value)
        return await self.write_data_async(loop=loop)

    # ========
    # Get
    def get(self, key: t.Any, default: t.Any = None, allow_cached_fallback: bool = False):
        if self._full_sync_only:
            return super().get(key=key, default=default)

        try:
            value = self.read_datum(key=key)
            if value is None:
                value = default
            else:
                self._data_dict[key] = value
        except Exception as ex:
            if not allow_cached_fallback:
                raise ex
            LOG.error(
                f"{type(self).__name__}: Returning cached value. Exception when trying to read datum from external: {ex}"
            )
            value = self._data_dict.get(key, default)

        return value

    async def get_async(
        self, key: t.Any, default: t.Any = None, loop: LoopType | None = None
    ) -> t.Any:
        return await call_sync_async(self.get, loop=loop, func_kwargs=dict(key=key, default=default))

    # ========
    # Set
    def _set(self, key: t.Any, value: t.Any, write: bool | None = None):
        result = super().set(key, value)
        if write == True or (write != False and self._write_on_update_default):
            self._update_external_on_change(key=key, value=value)
        return result

    def set(self, key: t.Any, value: t.Any, write: bool | None = None):
        return self._set(key=key, value=value, write=write)

    async def _set_async(
        self, key: t.Any, value: t.Any, write: bool | None = None, loop: LoopType | None = None
    ):
        result = await super().set_async(key, value)
        if write == True or (write != False and self._write_on_update_default):
            await self._update_external_on_change_async(key=key, value=value, loop=loop)
        return result

    async def set_async(
        self, key: t.Any, value: t.Any, write: bool | None = None, loop: LoopType | None = None
    ):
        return await self._set_async(key=key, value=value, write=write, loop=loop)

    # ========
    # Overwrite
    def overwrite_data(self, data: dict, write: bool | None = None) -> None:
        result = super().overwrite_data(data)
        self._update_external_on_change()
        return result

    # ========
    # Update
    def update_data(self, write: bool | None = None, **overrides: dict) -> None:
        result = super().update_data(**overrides)
        self._update_external_on_change()
        return result

    # ========
    # write_data

    @abstractmethod
    def write_data(self):
        """
        Write all key-value pairs to external location, fully overwriting/replacing
        """
        raise NotImplementedError()

    async def write_data_async(self, loop: LoopType | None = None):
        return await call_sync_async(self.write_data, loop=loop)

    # ========
    # write_datum

    @abstractmethod
    def write_datum(self, key: t.Any, value: t.Any):
        """
        WRite a single key-value pair to external location
        """
        if self._full_sync_only:
            raise NotImplementedError("Cannot read/write individual key-value pairs for this datastore backend type")
        raise NotImplementedError()

    async def write_datum_async(
        self, key: t.Any, value: t.Any | None = None, loop: LoopType | None = None
    ):
        return await call_sync_async(self.write_datum, loop=loop, func_kwargs=dict(key=key, value=value))

    # ========
    # read_data

    @abstractmethod
    def read_data(self) -> dict:
        """
        Read all key-value pairs from external location and return as a dict
        """
        raise NotImplementedError()

    async def read_data_async(self, loop: LoopType | None = None) -> dict:
        return await call_sync_async(self.read_data, loop=loop)

    # ========
    # read_datum

    @abstractmethod
    def read_datum(self, key: t.Any) -> t.Any:
        """
        Read a single key-value pair from external location
        """
        if self._full_sync_only:
            raise NotImplementedError("Cannot read/write individual key-value pairs for this datastore backend type")
        raise NotImplementedError()

    async def read_datum_async(self, key: t.Any, loop: LoopType | None = None) -> dict:
        return await call_sync_async(self.read_datum, loop=loop, func_kwargs=dict(key=key))


class BulkOnlyExternalBackend(ExternalBackend, metaclass=ABCMeta):
    """
    Safety subclass for use with external destinations that only support bulk/whole-dict writing (i.e.; files etc.)
    """

    _full_sync_only: bool = True

    # Make concrete, but not implemented
    def read_datum(self, key: t.Any) -> t.Any:
        raise NotImplementedError()

    # Make concrete, but not implemented
    def write_datum(self, key: t.Any, value: t.Any) -> t.Any:
        raise NotImplementedError()

    def _update_external_on_change(self, key: t.Any | None = None, value: t.Any | None = None):
        return self.write_data()

    async def _update_external_on_change_async(
        self,
        key: t.Any | None = None,
        value: t.Any | None = None,
        loop: LoopType | None = None,
    ):
        if (not self._full_sync_only) and key is not None and value is not None:
            return await self.write_datum_async(key=key, value=value)
        return await self.write_data_async(loop=loop)

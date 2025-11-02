from __future__ import annotations
import asyncio
import copy
import typing as t
from abc import ABC

from kvcommon import logger
from kvcommon.asynchronous.utils import call_sync_async


LOG = logger.get_logger("kvc-ds")


class DatastoreBackend(ABC):
    _data_dict: dict

    def __init__(self) -> None:
        self._data_dict = dict()

    def __str__(self) -> str:
        return f"<{type(self).__name__}>"

    # def __repr__(self) -> str:
    #     return f"<{type(self).__name__}>"

    @property
    def data(self) -> dict:
        """
        Return a COPY of the the dict containing this backend's data
        """
        return copy.deepcopy(self._data_dict)

    def get(self, key: t.Any, default: t.Any = None):
        """
        Get a key:value pair in the backend.
        """
        return self.data.get(key, default)

    async def get_async(
        self, key: t.Any, default: t.Any = None, loop: asyncio.AbstractEventLoop | None = None
    ) -> t.Any:
        return self.get(key=key, default=default)

    def set(self, key: t.Any, value: t.Any) -> None:
        self._data_dict[key] = value

    async def set_async(self, key: t.Any, value: t.Any) -> None:
        return self.set(key=key, value=value)

    def overwrite_data(self, data: dict) -> None:
        """
        Overwrite the entire contents of the backend's data with a new dict
        Guarantees a new dict, new ref
        """
        self._data_dict = copy.deepcopy(data)

    async def overwrite_data_async(self, data: dict, loop: asyncio.AbstractEventLoop | None = None) -> None:
        return await call_sync_async(self.overwrite_data, func_kwargs=dict(data=data), loop=loop)

    def update_data(self, **overrides: dict) -> None:
        """
        Update the backend's data dict with the contents of the overrides dict
        """
        data = self._data_dict
        data.update(overrides)
        # self.overwrite_data(data)

    async def update_data_async(self, loop: asyncio.AbstractEventLoop | None = None, **overrides: dict) -> None:
        return await call_sync_async(self.update_data, func_args=tuple(**overrides), loop=loop)

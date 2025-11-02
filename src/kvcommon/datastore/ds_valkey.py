from __future__ import annotations
import typing as t
from itertools import islice

try:
    import valkey
    import valkey.asyncio as valkey_asyncio
    from valkey.typing import EncodableT
    from valkey.typing import ResponseT

    VALKEY_AVAILABLE = True
except ImportError:
    VALKEY_AVAILABLE = False

from kvcommon.asynchronous.utils import LoopType
from kvcommon import logger

from .base import create_datastore
from .base import Datastore
from .ds_external import ExternalBackend


LOG = logger.get_logger("kvc-ds")


class ValkeyBackend(ExternalBackend):
    """
    # TODO: Handling for nested/complex data types
    """

    _file_extension: str = ".yaml"
    _client: valkey.Valkey
    _client_async: valkey_asyncio.Valkey
    _batch_size = 1000

    def __init__(
        self,
        valkey_client: valkey.Valkey,
        valkey_client_async: valkey_asyncio.Valkey,
        batch_size: int = 1000,
        write_on_update: bool = True,
    ) -> None:
        if not VALKEY_AVAILABLE:
            raise ImportError("valkey-py must be installed to use ValkeyBackend")

        super().__init__(write_on_update=write_on_update)

        self._client = valkey_client
        self._client_async = valkey_client_async
        self._batch_size = batch_size

    def ping(self) -> ResponseT:
        return self._client.ping()

    async def ping_async(self) -> ResponseT:
        return await self._client_async.ping()

    def disconnect(self):
        return self._client.close()

    async def disconnect_async(self):
        return await self._client_async.aclose()

    def write_data(self):
        return self._client.mset(self._data_dict)

    async def write_data_async(self):
        return await self._client_async.mset(self._data_dict)

    def write_datum(self, key: str, value: t.Any):
        return self._client.set(key, value)

    async def write_datum_async(self, key: str, value: EncodableT):
        return await self._client_async.set(key, value)

    def read_data(self) -> dict:
        client = self._client
        all_data = dict()
        key_iterator = client.scan_iter("*")

        while True:
            batch_keys = list(islice(key_iterator, self._batch_size))

            if not batch_keys:
                break
            batch_values = client.mget(batch_keys)

            for key, value in zip(batch_keys, batch_values):  # type: ignore
                all_data[key] = value

        return all_data

    async def read_data_async(self) -> dict:
        client = self._client_async
        batch_size = self._batch_size
        all_data = {}
        keys_batch = []

        async for key in client.scan_iter(match="*"):
            keys_batch.append(key)

            if len(keys_batch) >= batch_size:
                values = await client.mget(keys_batch)
                all_data.update(zip(keys_batch, values))
                keys_batch = []

        # Process any keys leftover in last batch
        if keys_batch:
            values = await client.mget(keys_batch)
            all_data.update(zip(keys_batch, values))

        return all_data

    def read_datum(self, key: str) -> t.Any:
        return self._client.get(key)

    async def read_datum_async(self, key: str) -> dict:
        return await self._client_async.get(key)


class ValkeyDatastore(Datastore):
    _backend_cls = ValkeyBackend
    _backend: ValkeyBackend


def create_valkey_datastore(
    config_version: int, host: str, port: int, db: int, write_on_update: bool = True
) -> Datastore:
    if not VALKEY_AVAILABLE:
        raise ImportError("valkey-py must be installed to use ValkeyDatastore")
    valkey_client = valkey.Valkey(host=host, port=port, db=db, decode_responses=True)
    valkey_client_async = valkey_asyncio.Valkey(host=host, port=port, db=db, decode_responses=True)
    backend = ValkeyBackend(
        valkey_client=valkey_client, valkey_client_async=valkey_client_async, write_on_update=write_on_update
    )
    return create_datastore(config_version, backend)

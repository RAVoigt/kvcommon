import mock

import fakeredis
import pytest

from kvcommon.datastore.ds_valkey import ValkeyBackend

from .test_backend_external import BackendTestSuite_External

from fakeredis import FakeValkey
from fakeredis import FakeAsyncValkey

@pytest.fixture
def backend():
    server = fakeredis.FakeServer()
    fakeredis_client = FakeValkey(server=server, decode_responses=True)
    fakeredis_client_async = FakeAsyncValkey(server=server, decode_responses=True)
    backend = ValkeyBackend(valkey_client=fakeredis_client, valkey_client_async=fakeredis_client_async)
    yield backend


class TestSuite_ValkeyBackend(BackendTestSuite_External):
    pass

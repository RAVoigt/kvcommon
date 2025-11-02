import pytest
from kvcommon.datastore.base import DatastoreBackend

from .base import BackendTestSuite


@pytest.fixture
def backend():
    return DatastoreBackend()


class TestSuite_DictBackend(BackendTestSuite):
    pass

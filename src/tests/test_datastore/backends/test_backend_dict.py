import pytest
from kvcommon.datastore.backend import DictBackend

from .base import BackendTestSuite


@pytest.fixture
def backend():
    return DictBackend()


class TestSuite_DictBackend(BackendTestSuite):
    pass
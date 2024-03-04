import mock

from pyfakefs.fake_filesystem_unittest import Patcher
from pyfakefs.fake_filesystem_unittest import TestCase
import pytest

from kvcommon.datastore.backend import TOMLBackend

from .test_backend_dict import BackendTestSuite



@pytest.fixture
def backend():
    patcher = Patcher()
    patcher.setUp()
    yield TOMLBackend(".", "_test.conf")
    patcher.tearDown()


class TestSuite_TOMLBackend(BackendTestSuite):
    pass

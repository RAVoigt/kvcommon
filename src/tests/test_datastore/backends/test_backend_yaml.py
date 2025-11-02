import mock

from pyfakefs.fake_filesystem_unittest import Patcher
from pyfakefs.fake_filesystem_unittest import TestCase
import pytest

from kvcommon.datastore.ds_yaml import YAMLBackend

from .test_backend_external import BackendTestSuite_External
from .test_backend_external import BulkOnlyBackendTestSuite_External


@pytest.fixture
def backend():
    patcher = Patcher()
    patcher.setUp()
    yield YAMLBackend(storage_dir_path=".", filename="_test.conf")
    patcher.tearDown()


class TestSuite_YAMLBackend(BulkOnlyBackendTestSuite_External):
    pass

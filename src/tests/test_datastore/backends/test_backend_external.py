import mock
import typing as t

from pyfakefs.fake_filesystem_unittest import Patcher
from pyfakefs.fake_filesystem_unittest import TestCase
import pytest
from pytest_mock.plugin import MockerFixture

from kvcommon.datastore.ds_external import ExternalBackend

from .test_backend_dict import BackendTestSuite


# @pytest.fixture
# def backend():
#     patcher = Patcher()
#     patcher.setUp()
#     test_backend = ExternalBackend()
#     yield test_backend
#     patcher.tearDown()


class BackendTestSuite_External(BackendTestSuite):

    def test_external_update_on_change(self, backend: ExternalBackend, mocker: MockerFixture):
        mock_spy_update = mocker.spy(backend, '_update_external_on_change')
        mock_spy_write_datum = mocker.spy(backend, 'write_datum')
        mock_spy_write_data = mocker.spy(backend, 'write_data')

        mock_spy_update.assert_not_called()
        mock_spy_write_datum.assert_not_called()
        mock_spy_write_data.assert_not_called()

        # Don't sync changes to external if write is False, even if default is True
        backend._write_on_update_default = True
        backend.set("key", "test", write=False)
        mock_spy_update.assert_not_called()

        # Sync changes to external if default is True and write is unspecified
        backend._write_on_update_default = True
        backend.set("key", "test")
        mock_spy_update.assert_called_once_with(key="key", value="test")
        mock_spy_update.reset_mock()

        # Sync changes to external if write is True, regardless of value of default
        backend._write_on_update_default = False
        backend.set("key", "test", write=True)
        mock_spy_update.assert_called_once_with(key="key", value="test")
        mock_spy_update.reset_mock()

    @pytest.mark.asyncio
    async def test_external_update_on_change_async(self, backend: ExternalBackend, mocker: MockerFixture):
        mock_spy_update = mocker.spy(backend, '_update_external_on_change_async')
        mock_spy_write_datum = mocker.spy(backend, 'write_datum')
        mock_spy_write_data = mocker.spy(backend, 'write_data')

        mock_spy_update.assert_not_called()
        mock_spy_write_datum.assert_not_called()
        mock_spy_write_data.assert_not_called()

        # Don't sync changes to external if write is False, even if default is True
        backend._write_on_update_default = True
        await backend.set_async("key", "test", write=False)
        mock_spy_update.assert_not_called()

        # Sync changes to external if default is True and write is unspecified
        backend._write_on_update_default = True
        await backend.set_async("key", "test")
        mock_spy_update.assert_called_once_with(key="key", value="test", loop=None)
        mock_spy_update.reset_mock()

        # Sync changes to external if write is True, regardless of value of default
        backend._write_on_update_default = False
        await backend.set_async("key", "test", write=True)
        mock_spy_update.assert_called_once_with(key="key", value="test", loop=None)
        mock_spy_update.reset_mock()

    def test_full_sync(self, backend: ExternalBackend, mocker: MockerFixture):
        mock_spy_update = mocker.spy(backend, '_update_external_on_change')
        mock_spy_write_datum = mocker.spy(backend, 'write_datum')
        mock_spy_write_data = mocker.spy(backend, 'write_data')

        mock_spy_update.assert_not_called()
        mock_spy_write_datum.assert_not_called()
        mock_spy_write_data.assert_not_called()

        backend._full_sync_only = False
        backend.set("key", "test", write=True)
        mock_spy_update.assert_called_once_with(key="key", value="test")
        mock_spy_write_datum.assert_called_once_with(key="key", value="test")
        mock_spy_write_data.assert_not_called()


class BulkOnlyBackendTestSuite_External(BackendTestSuite_External):

    def test_full_sync(self, backend: ExternalBackend, mocker: MockerFixture):
        mock_spy_update = mocker.spy(backend, '_update_external_on_change')
        mock_spy_write_datum = mocker.spy(backend, 'write_datum')
        mock_spy_write_data = mocker.spy(backend, 'write_data')

        mock_spy_update.assert_not_called()
        mock_spy_write_datum.assert_not_called()
        mock_spy_write_data.assert_not_called()

        # Ensure that write_datum doesn't get called in this subclass, even if _full_sync_only is set to False
        backend._full_sync_only = False
        backend.set("key", "test", write=True)
        mock_spy_write_datum.assert_not_called()
        mock_spy_write_data.assert_called_once_with()

        # Ensure that if single-datum methods somehow get called, they raise
        with pytest.raises(NotImplementedError):
            backend.write_datum("key", "test")
        with pytest.raises(NotImplementedError):
            backend.read_datum("key")

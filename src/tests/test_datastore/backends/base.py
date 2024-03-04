import pytest

from kvcommon.datastore.backend import DictBackend
from kvcommon.datastore.backend import DatastoreBackend


class BackendTestSuite:

    def test_get_method_without_by_ref(self, backend):
        backend.set("key", "value")
        result = backend.get("key")
        assert result == "value"

    def test_get_method_with_by_ref(self, backend):
        backend.set("key", "value")
        result = backend.get("key", by_ref=True)
        assert result == "value"

    def test_get_method_with_default_value(self, backend):
        result = backend.get("nonexistent_key", default="default_value")
        assert result == "default_value"

    def test_get_method_with_default_value_and_by_ref(self, backend):
        result = backend.get("nonexistent_key", default="default_value", by_ref=True)
        assert result == "default_value"

    def test_set_method(self, backend):
        backend.set("key", "value")
        assert backend._data_by_ref["key"] == "value"

    def test_overwrite_data_method(self, backend):
        data = {"key1": "value1", "key2": "value2"}
        backend.overwrite_data(data)
        assert backend._data_by_ref == data

    def test_update_data_method(self, backend):
        backend.set("key1", "value1")
        backend.update_data(key2="value2", key3="value3")
        expected_data = {"key1": "value1", "key2": "value2", "key3": "value3"}
        assert backend._data_by_ref == expected_data

    def test_data_copy_immutability(self, backend):
        backend.set("key", "value")
        data_copy = backend._data
        backend.set("key", "new_value")
        assert data_copy["key"] == "value"

    # def test_abstract_methods_raise_not_implemented_error():
    #     abstract_backend = DatastoreBackend()

    #     with pytest.raises(NotImplementedError, match=".*_data_by_ref.*"):
    #         abstract_backend._data_by_ref

    #     with pytest.raises(NotImplementedError, match=".*set.*"):
    #         abstract_backend.set("key", "value")

    #     with pytest.raises(NotImplementedError, match=".*overwrite_data.*"):
    #         abstract_backend.overwrite_data({"key": "value"})

    def test_set_method_overwrites_existing_value(self, backend):
        backend.set("key", "value")
        backend.set("key", "new_value")
        assert backend._data_by_ref["key"] == "new_value"

    def test_set_method_with_special_characters(self, backend):
        key = "!@#$%^&*()"
        value = "special_value"
        backend.set(key, value)
        assert backend._data_by_ref[key] == value

    def test_update_data_method_with_empty_dict(self, backend):
        backend.set("key1", "value1")
        backend.update_data()
        assert backend._data_by_ref == {"key1": "value1"}

    def test_get_method_with_empty_data(self, backend):
        result = backend.get("nonexistent_key")
        assert result is None

    def test_get_method_with_empty_data_and_default_value(self, backend):
        result = backend.get("nonexistent_key", default="default_value")
        assert result == "default_value"

    def test_get_method_with_empty_data_and_by_ref(self, backend):
        result = backend.get("nonexistent_key", by_ref=True)
        assert result is None

    def test_get_method_with_empty_data_and_default_value_and_by_ref(self, backend):
        result = backend.get("nonexistent_key", default="default_value", by_ref=True)
        assert result == "default_value"


# @pytest.fixture
# def dict_backend():
#     return DictBackend()


# def test_get_method_without_by_ref(dict_backend):
#     dict_backend.set("key", "value")
#     result = dict_backend.get("key")
#     assert result == "value"


# def test_get_method_with_by_ref(dict_backend):
#     dict_backend.set("key", "value")
#     result = dict_backend.get("key", by_ref=True)
#     assert result == "value"


# def test_get_method_with_default_value(dict_backend):
#     result = dict_backend.get("nonexistent_key", default="default_value")
#     assert result == "default_value"


# def test_get_method_with_default_value_and_by_ref(dict_backend):
#     result = dict_backend.get("nonexistent_key", default="default_value", by_ref=True)
#     assert result == "default_value"


# def test_set_method(dict_backend):
#     dict_backend.set("key", "value")
#     assert dict_backend._data_by_ref["key"] == "value"


# def test_overwrite_data_method(dict_backend):
#     data = {"key1": "value1", "key2": "value2"}
#     dict_backend.overwrite_data(data)
#     assert dict_backend._data_by_ref == data


# def test_update_data_method(dict_backend):
#     dict_backend.set("key1", "value1")
#     dict_backend.update_data(key2="value2", key3="value3")
#     expected_data = {"key1": "value1", "key2": "value2", "key3": "value3"}
#     assert dict_backend._data_by_ref == expected_data


# def test_data_copy_immutability(dict_backend):
#     dict_backend.set("key", "value")
#     data_copy = dict_backend._data
#     dict_backend.set("key", "new_value")
#     assert data_copy["key"] == "value"


# # def test_abstract_methods_raise_not_implemented_error():
# #     abstract_backend = DatastoreBackend()

# #     with pytest.raises(NotImplementedError, match=".*_data_by_ref.*"):
# #         abstract_backend._data_by_ref

# #     with pytest.raises(NotImplementedError, match=".*set.*"):
# #         abstract_backend.set("key", "value")

# #     with pytest.raises(NotImplementedError, match=".*overwrite_data.*"):
# #         abstract_backend.overwrite_data({"key": "value"})


# def test_set_method_overwrites_existing_value(dict_backend):
#     dict_backend.set("key", "value")
#     dict_backend.set("key", "new_value")
#     assert dict_backend._data_by_ref["key"] == "new_value"


# def test_set_method_with_special_characters(dict_backend):
#     key = "!@#$%^&*()"
#     value = "special_value"
#     dict_backend.set(key, value)
#     assert dict_backend._data_by_ref[key] == value


# def test_update_data_method_with_empty_dict(dict_backend):
#     dict_backend.set("key1", "value1")
#     dict_backend.update_data()
#     assert dict_backend._data_by_ref == {"key1": "value1"}


# def test_get_method_with_empty_data(dict_backend):
#     result = dict_backend.get("nonexistent_key")
#     assert result is None


# def test_get_method_with_empty_data_and_default_value(dict_backend):
#     result = dict_backend.get("nonexistent_key", default="default_value")
#     assert result == "default_value"


# def test_get_method_with_empty_data_and_by_ref(dict_backend):
#     result = dict_backend.get("nonexistent_key", by_ref=True)
#     assert result is None


# def test_get_method_with_empty_data_and_default_value_and_by_ref(dict_backend):
#     result = dict_backend.get("nonexistent_key", default="default_value", by_ref=True)
#     assert result == "default_value"

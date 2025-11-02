import pytest


class BackendTestSuite:

    def test_get(self, backend):
        backend.set("key", "value")
        result = backend.get("key")

        assert result == "value"

    @pytest.mark.asyncio
    async def test_get_async(self, backend):
        backend.set("key", "value")
        result = await backend.get_async("key")
        assert result == "value"

    def test_get_with_default_value(self, backend):
        result = backend.get("nonexistent_key", default="default_value")
        assert result == "default_value"

    @pytest.mark.asyncio
    async def test_get_async_with_default_value(self, backend):
        result = await backend.get_async("nonexistent_key", default="default_value")
        assert result == "default_value"

    def test_set(self, backend):
        backend.set("key", "value")
        assert backend._data_dict["key"] == "value"

    @pytest.mark.asyncio
    async def test_set_async(self, backend):
        await backend.set_async("key", "value")
        assert backend._data_dict["key"] == "value"

    def test_update_data(self, backend):
        backend.set("key1", "value1")
        backend.update_data(key2="value2", key3="value3")
        expected_data = {"key1": "value1", "key2": "value2", "key3": "value3"}
        assert backend._data_dict == expected_data

    def test_data_copy_immutability(self, backend):
        backend.set("key", "value")
        data_copy = backend.data
        backend.set("key", "new_value")
        assert data_copy["key"] == "value"

    def test_set_overwrites_existing_value(self, backend):
        backend.set("key", "value")
        backend.set("key", "new_value")
        assert backend._data_dict["key"] == "new_value"

    def test_set_with_special_characters(self, backend):
        key = "!@#$%^&*()"
        value = "special_value"
        backend.set(key, value)
        assert backend._data_dict[key] == value

    def test_update_data_with_empty_dict(self, backend):
        backend.set("key1", "value1")
        backend.update_data()
        assert backend._data_dict == {"key1": "value1"}

    @pytest.mark.asyncio
    async def test_update_data_async_with_empty_dict(self, backend):
        backend._data_dict["key1"] = "value1"
        await backend.update_data_async()
        assert backend._data_dict == {"key1": "value1"}

    def test_overwrite_data(self, backend):
        backend._data_dict["key1"] = "value1"
        assert backend._data_dict == {"key1": "value1"}
        backend.overwrite_data(dict(key2="value2", key3="value3"))
        assert backend._data_dict == {"key2": "value2", "key3": "value3"}

    @pytest.mark.asyncio
    async def test_overwrite_data_async(self, backend):
        backend._data_dict["key1"] = "value1"
        assert backend._data_dict == {"key1": "value1"}
        await backend.overwrite_data_async(dict(key2="value2", key3="value3"))
        assert backend._data_dict == {"key2": "value2", "key3": "value3"}

    def test_get_with_empty_data(self, backend):
        result = backend.get("nonexistent_key")
        assert result is None

    def test_get_with_empty_data_and_default_value(self, backend):
        result = backend.get("nonexistent_key", default="default_value")
        assert result == "default_value"

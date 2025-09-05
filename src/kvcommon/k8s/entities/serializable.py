from __future__ import annotations

import typing as t

from kvcommon.exceptions import InvalidDataException
from kvcommon.misc.entities import SerializableObject


from kvcommon.logger import get_logger

LOG = get_logger("kvc-k8s")


class K8sSerializable(SerializableObject):
    def _get_essential_str(self, key: str, default: str | None = None) -> str:
        value = self._deserialized.get(key, default)
        if not value and default is None:
            raise InvalidDataException(f"{self.__class__.__name__} must have a {key}")
        return value

    def _initialize_dict_values(self, value_keys: str | list[str] | set[str] | tuple[str]):
        if isinstance(value_keys, str):
            self._deserialized[value_keys] = self._deserialized.get(value_keys, {})
        elif isinstance(value_keys, list|set|tuple):
            for value_key in value_keys:
                self._initialize_dict_values(value_keys=value_key)
        else:
            TypeError("value_keys must be a str or list/set/tuple of str")

    def _initialize_list_values(self, value_keys: str | list[str] | set[str] | tuple[str]):
        if isinstance(value_keys, str):
            self._deserialized[value_keys] = self._deserialized.get(value_keys, [])
        elif isinstance(value_keys, list|set|tuple):
            for value_key in value_keys:
                self._initialize_list_values(value_keys=value_key)
        else:
            TypeError("value_keys must be a str or list/set/tuple of str")

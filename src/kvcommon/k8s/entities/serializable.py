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

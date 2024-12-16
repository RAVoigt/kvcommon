from __future__ import annotations

import base64
import typing as t

from kubernetes.client.models.v1_secret import V1Secret

from kvcommon.exceptions import K8sException
from kvcommon.types import to_bool

from .base import K8sObject


from kvcommon.logger import get_logger

LOG = get_logger("kvc-k8s")


class Secret(K8sObject):
    _expected_kind = "Secret"
    _spec: None
    _status: None

    def __init__(self, serialized: str, deserialized: dict) -> None:
        super().__init__(serialized, deserialized)
        self._spec = None
        self._status = None

    @classmethod
    def from_model(cls, model: V1Secret) -> t.Self:
        return cls.from_dict(model.to_dict())

    def to_model(self) -> V1Secret:
        return V1Secret(**self._deserialized)

    @property
    def type(self) -> str:
        return self._get_essential_str("type")

    @property
    def data(self) -> dict[str, str]:
        # b64-encoded data
        return self._deserialized.get("data", {})

    @property
    def data_keys(self) -> set[str]:
        return set(self.data.keys())

    @property
    def string_data(self) -> dict[str, str]:
        # decoded string data (Typically empty if retrieved from a Secret in cluster)
        string_data = self._deserialized.get("string_data", None)
        if string_data is not None:
            return string_data
        data = self.data
        decoded_data = dict()
        for key, value in data.items():
            try:
                decoded_data[key] = base64.b64decode(value).decode("utf-8")
            except binascii.error as ex:  # type: ignore
                raise K8sException(
                    f"Failed to b64decode value at key: '{key}' in data for secret with name: '{value}'.\n"
                    f"base64 exception: {ex}"
                )
        return decoded_data

    @property
    def string_data_keys(self) -> set[str]:
        return set(self.string_data.keys())

    @property
    def immutable(self) -> bool:
        return to_bool(self._deserialized.get("immutable", False))

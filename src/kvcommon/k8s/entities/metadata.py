from __future__ import annotations

import dataclasses
import json
import typing as t

from .. import InvalidDataException
from .base import K8sSerializable

from kvcommon.logger import get_logger


LOG = get_logger("kvc-k8s")


class Metadata(K8sSerializable):

    def get(self, metadata_key: str, default: t.Any = None) -> str | dict | list | None:
        value = self._deserialized.get(metadata_key, default)

        if not isinstance(value, (str, dict, list)):
            raise InvalidDataException(
                f"K8s Metadata with unexpected type ({type(value)}) at key: '{metadata_key}'"
            )
        return value

    def __repr__(self):
        return f"<Metadata: ns:'{self.namespace}' | name:'{self.name}'"

    @property
    def name(self) -> str:
        return self._get_essential_str("name")

    @property
    def namespace(self) -> str:
        return self._get_essential_str("namespace")

    @property
    def uid(self) -> str:
        return self._get_essential_str("uid")

    @property
    def annotations(self) -> dict:
        return self._deserialized.get("annotations", {})

    @property
    def labels(self) -> dict:
        return self._deserialized.get("labels", {})

    @property
    def finalizers(self) -> list[str]:
        return self._deserialized.get("finalizers", {})

    @property
    def managed_fields(self) -> list[dict]:
        return self._deserialized.get("managed_fields", {})

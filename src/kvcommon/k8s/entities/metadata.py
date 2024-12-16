from __future__ import annotations

from datetime import datetime
import typing as t

from kubernetes.client.models.v1_object_meta import V1ObjectMeta

from kvcommon.exceptions import InvalidDataException

from .serializable import K8sSerializable

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

    @classmethod
    def from_model(cls, model: V1ObjectMeta) -> t.Self:
        return cls.from_dict(model.to_dict())

    def to_model(self) -> V1ObjectMeta:
        return V1ObjectMeta(**self._deserialized)

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
    def creation_timestamp(self) -> datetime | None:
        datetime_str = self._deserialized.get(
            "creation_timestamp",
        )
        if datetime_str is not None:
            return datetime.fromisoformat(datetime_str)

    @property
    def labels(self) -> dict:
        return self._deserialized.get("labels", {})

    @property
    def finalizers(self) -> list[str]:
        return self._deserialized.get("finalizers", {})

    @property
    def managed_fields(self) -> list[dict]:
        return self._deserialized.get("managed_fields", {})

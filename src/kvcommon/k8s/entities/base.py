from __future__ import annotations

import typing as t

from kvcommon.exceptions import InvalidDataException
from kvcommon.exceptions import K8sException

from .metadata import Metadata
from .serializable import K8sSerializable

from kvcommon.logger import get_logger

LOG = get_logger("kvc-k8s")


class K8sObjectSpec(K8sSerializable):
    pass


class K8sObjectStatus(K8sSerializable):
    pass


class K8sObject(K8sSerializable):
    """
    Base class for K8s objects to make them easier to work with in non-str form.
    Adds typehinting and convenience methods that are lacking from models in kubernetes lib.

    Mostly private attrs to imply immutability.
    """

    _raw: str
    _api_version: str | None
    _kind: str | None
    _metadata: Metadata
    _spec: K8sObjectSpec
    _status: K8sObjectStatus
    _is_namespaced: bool = True

    _expected_kind: str | None = None

    def __init__(self, serialized: str, deserialized: dict) -> None:
        super().__init__(serialized=serialized, deserialized=deserialized)

        self._api_version = deserialized.get("api_version", None)
        self._metadata = Metadata.from_dict(deserialized.get("metadata", {}))
        self._spec = K8sObjectSpec.from_dict(deserialized.get("spec", {}))
        self._status = deserialized.get("status", {})
        self._kind = deserialized.get("kind", None)
        if self._expected_kind is not None:
            if self._kind != self._expected_kind:
                raise InvalidDataException(
                    f"Input data has wrong 'Kind' for {self.__class__.__name__}"
                )

    def __repr__(self):
        return f"<{self.__class__.__name__}: ns:'{self.namespace}' | name:'{self.name}'"

    def __hash__(self):
        if self._is_namespaced:
            namespace = self.metadata.namespace
        else:
            namespace = "None"
        return hash((self._kind, self.metadata.name, namespace))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        if not hasattr(other, "is_namespaced") or self._is_namespaced != other.is_namespaced:
            return False
        if self._is_namespaced:
            return (
                self._kind == other.kind
                and self.name == other.name
                and self.namespace == other.namespace
            )
        return self._kind == other.kind and self.name == other.name

    @property
    def api_version(self) -> str | None:
        return self._api_version
        # return self._get_essential_str("api_version")

    @property
    def kind(self) -> str | None:
        return self._kind
        # return self._get_essential_str("kind")

    @property
    def spec(self) -> K8sObjectSpec:
        return self._spec.copy()

    @property
    def status(self) -> K8sObjectStatus:
        return self._status.copy()

    # ==== Metadata

    def get_metadata_attr(self, attr_key: str, default: t.Any = None) -> str | dict | list | None:
        return self._metadata.get(attr_key, default)

    @property
    def metadata(self) -> Metadata:
        return self._metadata.copy()

    @property
    def name(self) -> str:
        return self._metadata.name

    @property
    def namespace(self) -> str:
        if not self.is_namespaced:
            raise K8sException(f"Object of type '{self.__class__.__name__}' is not namespaced")
        return self._metadata.namespace

    @property
    def is_namespaced(self) -> bool:
        return self._is_namespaced and self._metadata.namespace is not None

    @property
    def uid(self) -> str:
        return self._metadata.uid

    @property
    def annotations(self) -> dict:
        return self._metadata.annotations

    @property
    def labels(self) -> dict:
        return self._metadata.labels

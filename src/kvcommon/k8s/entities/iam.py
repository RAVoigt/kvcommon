from __future__ import annotations
import typing as t

from .serializable import K8sSerializable


class IAMBinding(K8sSerializable):
    def __repr__(self):
        return f"<{self.__class__.__name__}: role:'{self.role}' | members:'{self.members}'"

    @property
    def role(self) -> str | None:
        return self._get_essential_str("role")

    @property
    def members(self) -> list[str]:
        return self._deserialized.get("members", [])


class IAMPolicy(K8sSerializable):

    def __repr__(self):
        return f"<{self.__class__.__name__}: bindings:'{self.bindings}'"

    @property
    def version(self) -> str:
        return self._get_essential_str("version")

    @property
    def etag(self) -> str:
        return self._get_essential_str("etag")

    @property
    def bindings(self) -> list[IAMBinding]:
        bindings_list = self._deserialized.get("bindings", [])
        return [IAMBinding.from_dict(binding) for binding in bindings_list]

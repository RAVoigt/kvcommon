from __future__ import annotations
import typing as t

from kubernetes.client.models.v1_pod_template import V1PodTemplate

from .base import K8sObject
from .base import K8sObjectSpec
from .metadata import Metadata

from kvcommon.logger import get_logger

LOG = get_logger("kvc-k8s")


# This is confusing, but PodTemplateSpec has its own minimal spec
class Spec_PodTemplate_Spec(K8sObjectSpec):
    _meta: Metadata
    _spec: K8sObjectSpec

    def __init__(self, serialized: str, deserialized: dict) -> None:
        super().__init__(serialized=serialized, deserialized=deserialized)
        self._meta = Metadata.from_dict(deserialized.get("metadata", {}))
        self._spec = K8sObjectSpec.from_dict(deserialized.get("spec", {}))


class Spec_PodTemplate(K8sObject): # Note: K8sObject, not K8sObjectSpec
    # Ref: V1PodTemplateSpec
    _spec: K8sObjectSpec

    def __init__(self, serialized: str, deserialized: dict) -> None:
        super().__init__(serialized=serialized, deserialized=deserialized)
        self._spec = K8sObjectSpec.from_dict(deserialized.get("spec", {}))


class PodTemplate(K8sObject):
    _spec: Spec_PodTemplate

    def __init__(self, serialized: str, deserialized: dict) -> None:
        super().__init__(serialized=serialized, deserialized=deserialized)
        self._spec = Spec_PodTemplate.from_dict(deserialized.get("spec", {}))

    @classmethod
    def from_model(cls, model: V1PodTemplate) -> t.Self:
        return super().from_model(model=model)

    def to_model(self) -> V1PodTemplate:
        model_obj = super().to_model(model_cls=V1PodTemplate)
        if not isinstance(model_obj, V1PodTemplate):
            raise TypeError(f"Unexpected type from deserialization to model: {type(model_obj).__name__}")
        return model_obj

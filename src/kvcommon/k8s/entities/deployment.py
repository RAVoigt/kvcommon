from __future__ import annotations

import typing as t

from kubernetes.client.models.v1_deployment import V1Deployment
from kubernetes.client.models.v1_label_selector import V1LabelSelector
from kubernetes.client.models.v1_deployment_strategy import V1DeploymentStrategy


from .base import K8sObject
from .base import K8sObjectSpec
from .metadata import Metadata
from .pod_template import PodTemplate

from kvcommon.logger import get_logger


LOG = get_logger("kvc-k8s")


class DeploymentMetadata(Metadata):
    pass


class Spec_Deployment(K8sObjectSpec):
    # Ref: V1DeploymentSpec

    _template: PodTemplate

    def __init__(self, serialized: str, deserialized: dict) -> None:
        super().__init__(serialized=serialized, deserialized=deserialized)
        self._template = PodTemplate.from_dict(deserialized.get("template", {}))

    @property
    def min_ready_seconds(self) -> int:
        return self._get_internal("min_ready_seconds")

    @property
    def progress_deadline_seconds(self) -> int:
        return self._get_internal("paused")

    @property
    def paused(self) -> bool:
        return self._get_internal("paused")

    @property
    def replicas(self) -> int:
        return self._get_internal("replicas")

    @property
    def revision_history_limit(self) -> int:
        return self._get_internal("revision_history_limit")

    @property
    def selector(self) -> V1LabelSelector:
        return self._get_internal("selector")

    @property
    def strategy(self) -> V1DeploymentStrategy:
        return self._get_internal("strategy")

    @property
    def template(self) -> PodTemplate:
        return self._template


class Deployment(K8sObject):
    _expected_kind = "Deployment"
    _spec: Spec_Deployment

    def __init__(self, serialized: str, deserialized: dict) -> None:
        super().__init__(serialized=serialized, deserialized=deserialized)
        self._meta = DeploymentMetadata.from_dict(deserialized.get("metadata", {}))
        self._spec = Spec_Deployment.from_dict(deserialized.get("spec", {}))

    @classmethod
    def from_model(cls, model: V1Deployment) -> t.Self:
        return super().from_model(model=model)

    def to_model(self) -> V1Deployment:
        model_obj = super().to_model(model_cls=V1Deployment)
        if not isinstance(model_obj, V1Deployment):
            raise TypeError(f"Unexpected type from deserialization to model: {type(model_obj).__name__}")
        return model_obj

    @property
    def spec(self) -> Spec_Deployment:
        return self._spec.copy()

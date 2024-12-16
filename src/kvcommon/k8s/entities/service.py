from __future__ import annotations

import typing as t

from kubernetes.client.models.v1_service import V1Service

from .base import K8sObject
from .base import K8sObjectSpec
from .base import K8sObjectStatus
from .ingress import IngressLoadBalancer
from .serializable import K8sSerializable

from kvcommon.logger import get_logger

LOG = get_logger("kvc-k8s")


class ServiceLoadBalancer(IngressLoadBalancer):
    pass


class Status_Service(K8sObjectStatus):
    @property
    def status_load_balancers(self) -> list[ServiceLoadBalancer]:
        load_balancer = self._deserialized.get("load_balancer", {})
        lb_list = load_balancer.get("ingress", [])
        lb_obj_list = []
        for lb_json in lb_list:
            lb_obj_list.append(ServiceLoadBalancer.from_dict(lb_json))
        return lb_obj_list

    @property
    def ips(self) -> list[str]:
        return [lb.ip for lb in self.status_load_balancers if lb.ip is not None]

    @property
    def conditions(self) -> t.Any:
        return self._deserialized.get("conditions", None)


class ServicePort(K8sSerializable):
    @property
    def app_protocol(self) -> str:
        return self._deserialized.get("clustapp_protocoler_ip", None)

    @property
    def name(self) -> int:
        return self._deserialized.get("name", None)

    @property
    def node_port(self) -> int:
        return self._deserialized.get("node_port", None)

    @property
    def port(self) -> int:
        return self._deserialized.get("port", None)

    @property
    def protocol(self) -> str:
        return self._deserialized.get("protocol", None)

    @property
    def target_port(self) -> int:
        return self._deserialized.get("target_port", None)


class Spec_Service(K8sObjectSpec):
    @property
    def cluster_ip(self) -> str:
        return self._get_essential_str("cluster_ip")

    @property
    def cluster_ips(self) -> list[str]:
        return self._deserialized.get("cluster_i_ps", None)

    @property
    def external_ips(self) -> list[str]:
        return self._deserialized.get("external_i_ps", None)

    @property
    def external_traffic_policy(self) -> str | None:
        return self._deserialized.get("external_traffic_policy", None)

    @property
    def health_check_node_port(self) -> str | None:
        return self._deserialized.get("health_check_node_port", None)

    @property
    def internal_traffic_policy(self) -> str | None:
        return self._deserialized.get("internal_traffic_policy", None)

    @property
    def ip_families(self) -> list[str]:
        return self._deserialized.get("ip_families", None)

    @property
    def ip_family_policy(self) -> str | None:
        return self._deserialized.get("ip_family_policy", None)

    @property
    def load_balancer_class(self) -> str | None:
        return self._deserialized.get("load_balancer_class", None)

    @property
    def load_balancer_ip(self) -> str | None:
        return self._deserialized.get("load_balancer_ip", None)

    @property
    def load_balancer_source_ranges(self) -> str | None:
        return self._deserialized.get("load_balancer_source_ranges", None)

    @property
    def ports(self) -> list[ServicePort]:
        ports_list = self._deserialized.get("ports", None)
        return [ServicePort.from_dict(port) for port in ports_list]

    @property
    def publish_not_ready_addresses(self) -> str | None:
        return self._deserialized.get("publish_not_ready_addresses", None)

    @property
    def selector(self) -> dict | None:
        return self._deserialized.get("selector", None)

    @property
    def session_affinity(self) -> str | None:
        return self._deserialized.get("session_affinity", None)

    @property
    def session_affinity_config(self) -> str | None:
        return self._deserialized.get("session_affinity_config", None)

    @property
    def traffic_distribution(self) -> str | None:
        return self._deserialized.get("traffic_distribution", None)

    @property
    def app_kubernetes_io_instance(self) -> str | None:
        return self._deserialized.get("app.kubernetes.io/instance", None)

    @property
    def app_kubernetes_io_name(self) -> str | None:
        return self._deserialized.get("app.kubernetes.io/name", None)

    @property
    def type(self) -> str:
        return self._get_essential_str("type")


class Service_Annotation_BackendConfig(K8sSerializable):
    @property
    def default(self) -> str | None:
        # Same backendconfig for all ports
        # https://cloud.google.com/kubernetes-engine/docs/how-to/ingress-configuration#same_backendconfig_for_all_service_ports
        return self._deserialized.get("default", None)

    @property
    def ports(self) -> dict[str, str]:
        # Backendconfig per service port
        # https://cloud.google.com/kubernetes-engine/docs/how-to/ingress-configuration#unique_backendconfig_per_service_port
        return self._deserialized.get("ports", {})


class Service_Annotation_NEG(K8sSerializable):
    @property
    def ingress(self) -> bool | None:
        return self._deserialized.get("ingress", None)


class Service(K8sObject):
    _expected_kind = "Service"
    _spec: Spec_Service
    _status: Status_Service

    def __init__(self, serialized: str, deserialized: dict) -> None:
        super().__init__(serialized, deserialized)
        self._spec = Spec_Service.from_dict(deserialized.get("spec", {}))
        self._status = Status_Service.from_dict(deserialized.get("status", {}))

    @classmethod
    def from_model(cls, model: V1Service) -> t.Self:
        return cls.from_dict(model.to_dict())

    @property
    def backend_config_annotation(self) -> Service_Annotation_BackendConfig:
        beta_annotation = self.annotations.get("beta.cloud.google.com/backend-config", {})
        annotation = self.annotations.get("cloud.google.com/backend-config", beta_annotation)
        return Service_Annotation_BackendConfig.from_dict(annotation)

    @property
    def neg_annotation(self) -> Service_Annotation_NEG | None:
        annotation = self.annotations.get("cloud.google.com/neg", None)
        if annotation is not None:
            # TODO: json/dict?
            return Service_Annotation_NEG.from_json(annotation)
        return None

    @property
    def is_ingress_neg(self) -> bool:
        """
        Returns true if Service has the GKE Network Endpoint Group annotation for Ingress
        """
        neg = self.neg_annotation
        if neg is not None:
            return neg.ingress or False
        return False

    @property
    def cluster_ip(self) -> str:
        return self._spec.cluster_ip

    @property
    def external_traffic_policy(self) -> str | None:
        return self._spec.external_traffic_policy

    @property
    def internal_traffic_policy(self) -> str | None:
        return self._spec.internal_traffic_policy

    @property
    def ports(self) -> list[ServicePort]:
        return self._spec.ports

    @property
    def selector(self) -> dict | None:
        selector = self._spec.selector
        if selector is None:
            return
        return selector.copy()

    @property
    def type(self) -> str:
        return self._spec.type

    def get_backend_config_names(self) -> set[str]:
        backendconfig_names = set()
        annot = self.backend_config_annotation

        if annot.default is not None:
            backendconfig_names.add(annot.default)

        for bec_name in annot.ports.values():
            backendconfig_names.add(bec_name)
        return backendconfig_names

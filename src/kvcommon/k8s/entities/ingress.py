from __future__ import annotations

import dataclasses
import json
import typing as t

from kubernetes.client.models.v1_ingress import V1Ingress

from .base import K8sObject
from .base import K8sObjectSpec
from .base import K8sObjectStatus
from .serializable import K8sSerializable

from kvcommon.logger import get_logger

LOG = get_logger("kvc-k8s")


class IngressBackend_Resource(K8sSerializable):
    # https://kubernetes.io/docs/concepts/services-networking/ingress/#resource-backend

    @property
    def apiGroup(self) -> str | None:
        return self._deserialized.get("apiGroup", None)

    @property
    def kind(self) -> str | None:
        return self._deserialized.get("kind", None)

    @property
    def name(self) -> str | None:
        return self._deserialized.get("name", None)


class IngressBackend_Service_Port(K8sSerializable):
    @property
    def name(self) -> str | None:
        return self._deserialized.get("name", None)

    @property
    def number(self) -> int:
        return int(self._get_essential_str("number"))


class IngressBackend_Service(K8sSerializable):
    """
    Represents only a spec.rules[n].http.paths[n].backend.service dict in an Ingress
    NOT the actual, full K8s service object
    """

    # https://kubernetes.io/docs/concepts/services-networking/ingress/#resource-backend
    @property
    def name(self) -> str:
        # K8s service name as backend to Ingress path
        return self._get_essential_str("name")

    @property
    def port(self) -> IngressBackend_Service_Port:
        return IngressBackend_Service_Port.from_dict(self._deserialized.get("port", {}))


class IngressBackend(K8sSerializable):
    """
    Represents only a spec.rules[n].http.paths[n].backend dict in an Ingress
    NOT a BackendConfig
    """

    @property
    def resource(self) -> IngressBackend_Resource | None:
        resource = self._deserialized.get("resource", None)
        if resource is not None:
            return IngressBackend_Resource.from_dict(resource)

    @property
    def service(self) -> IngressBackend_Service | None:
        service = self._deserialized.get("service", None)
        if service is not None:
            return IngressBackend_Service.from_dict(service)

    @property
    def has_resource(self) -> bool:
        return self.resource is not None

    @property
    def has_service(self) -> bool:
        return self.service is not None


class IngressPath(K8sSerializable):
    """
    Represents a spec.rules[n].http.paths[n] dict in an Ingress
    """

    @property
    def path(self) -> str | None:
        return self._deserialized.get("path", None)

    @property
    def path_type(self) -> str | None:
        return self._deserialized.get("path_type", None)

    @property
    def backend(self) -> IngressBackend:
        backend = self._deserialized.get("backend", {})
        return IngressBackend.from_dict(backend)

    @property
    def has_resource(self) -> bool:
        return self.backend.has_resource

    @property
    def has_service(self) -> bool:
        return self.backend.has_service

    def get_service(self) -> IngressBackend_Service | None:
        return self.backend.service

    def get_resource(self) -> IngressBackend_Resource | None:
        return self.backend.resource


class IngressRule(K8sSerializable):
    """
    Represents a spec.rules[n] dict in an Ingress
    """

    @property
    def host(self) -> str:
        return self._get_essential_str("host")

    @property
    def paths(self) -> list[IngressPath]:
        http = self._deserialized.get("http", {})
        paths = http.get("paths", [])
        return [IngressPath.from_dict(path) for path in paths]

    def get_all_resources_by_path(self) -> dict[str, IngressBackend_Resource]:
        resources_by_path = dict()
        for path in self.paths:
            resource = path.get_resource()
            if resource is None:
                continue
            resources_by_path[path] = resource
        return resources_by_path

    def get_all_services_by_path(self) -> dict[str, IngressBackend_Service]:
        services_by_path = dict()
        for path in self.paths:
            service = path.get_service()
            if service is None:
                continue
            services_by_path[path] = service
        return services_by_path


class IngressLoadBalancer(K8sSerializable):
    @property
    def hostname(self) -> str | None:
        return self._deserialized.get("hostname", None)

    @property
    def ip(self) -> str | None:
        return self._deserialized.get("ip", None)

    @property
    def ports(self) -> str | list[str] | None:
        return self._deserialized.get("ports", None)


class Status_Ingress(K8sObjectStatus):
    @property
    def status_load_balancers(self) -> list[IngressLoadBalancer]:
        load_balancer = self._deserialized.get("load_balancer", {})
        lb_list = load_balancer.get("ingress", [])
        lb_obj_list = []
        for lb_json in lb_list:
            lb_obj_list.append(IngressLoadBalancer.from_dict(lb_json))
        return lb_obj_list

    @property
    def ips(self) -> list[str]:
        return [lb.ip for lb in self.status_load_balancers if lb.ip is not None]


class Spec_Ingress(K8sObjectSpec):
    @property
    def default_backend(self) -> str | None:
        return self._deserialized.get("default_backend", None)

    @property
    def ingress_class_name(self) -> str | None:
        return self._deserialized.get("ingress_class_name", None)

    @property
    def tls(self) -> str | None:
        return self._deserialized.get("tls", None)

    @property
    def rules(self) -> list[IngressRule]:
        rules_list = self._deserialized.get("rules", [])
        return [IngressRule.from_dict(rule) for rule in rules_list]

    def get_all_hosts(self) -> list[str]:
        hosts = []
        for rule in self.rules:
            hosts.append(rule.host)
        return hosts

    def get_all_paths_by_host(self) -> dict[str, list[IngressPath]]:
        paths_by_host = dict()
        for rule in self.rules:
            paths_by_host[rule.host] = []
            paths_by_host[rule.host].append(rule.paths.copy())
        return paths_by_host

    def get_all_paths_by_rule(self) -> dict[IngressRule, list[IngressPath]]:
        paths_by_host = dict()
        for rule in self.rules:
            paths_by_host[rule] = []
            paths_by_host[rule].append(rule.paths.copy())
        return paths_by_host

    def get_all_services_by_path_by_host(self) -> dict[str, dict[str, IngressBackend_Service]]:
        services_by_path_by_host = dict()
        for rule in self.rules:
            services_by_path_by_host[rule.host] = rule.get_all_services_by_path()
        return services_by_path_by_host

    def get_all_services(self) -> list[IngressBackend_Service]:
        services = []
        for rule in self.rules:
            for path in rule.paths:
                service = path.backend.service
                if service is None:
                    continue
                services.append(service)
        return services

    def get_all_service_names(self) -> set[str]:
        names = [service.name for service in self.get_all_services()]
        return set(names)


@dataclasses.dataclass(kw_only=True)
class Ingress_Annotation_Backend:
    name: str
    status: str


class Ingress(K8sObject):
    _expected_kind = "Ingress"
    _spec: Spec_Ingress
    _status: Status_Ingress

    def __init__(self, serialized: str, deserialized: dict) -> None:
        super().__init__(serialized, deserialized)
        self._spec = Spec_Ingress.from_dict(deserialized.get("spec", {}))
        self._status = Status_Ingress.from_dict(deserialized.get("status", {}))

    @classmethod
    def from_model(cls, model: V1Ingress) -> t.Self:
        return cls.from_dict(model.to_dict())

    @property
    def rules(self) -> list[IngressRule]:
        return self._spec.rules

    @property
    def ips(self) -> list[str]:
        return self._status.ips.copy()

    @property
    def backend_annotations(self) -> dict[str, Ingress_Annotation_Backend]:
        backends_json = self.annotations.get("ingress.kubernetes.io/backends", None)
        backends = dict()
        if backends_json is not None:
            backends_dict = json.loads(backends_json)
            for backend_name, backend_status in backends_dict.items():
                backends[backend_name] = Ingress_Annotation_Backend(
                    name=backend_name,
                    status=backend_status,
                )
        return backends

    def get_all_paths_by_host(self) -> dict[str, list[IngressPath]]:
        return self._spec.get_all_paths_by_host()

    def get_all_services_by_path_by_host(self) -> dict[str, dict[str, IngressBackend_Service]]:
        return self._spec.get_all_services_by_path_by_host()

    def get_all_services(self) -> list[IngressBackend_Service]:
        return self._spec.get_all_services()

    def get_all_service_names(self) -> set[str]:
        return self._spec.get_all_service_names()

    def to_google_model(self):
        return V1Ingress(
            api_version=self.api_version,
            kind=self.kind,
            metadata=self.metadata.to_dict(),
            spec=self.spec.to_dict(),
            status=self.status.to_dict(),
        )

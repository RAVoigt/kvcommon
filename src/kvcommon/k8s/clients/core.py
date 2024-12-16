from kubernetes.client import CoreV1Api
from kubernetes.client.exceptions import ApiException
from kubernetes.client.models.v1_secret import V1Secret
from kubernetes.client.models.v1_service import V1Service
from kubernetes.client.models.v1_service_list import V1ServiceList

from kvcommon.exceptions import K8sException
from kvcommon.k8s.entities.ingress import Ingress
from kvcommon.k8s.entities.secret import Secret
from kvcommon.k8s.entities.service import Service
from .base import K8sClientBase

from kvcommon.logger import get_logger

LOG = get_logger("kvc-k8s")


class K8sCoreClient(K8sClientBase[CoreV1Api]):
    """
    The kubernetes client is maddeningly opaque when it comes to typing and return values.

    Wrap the parts of it we're using in a convenience layer with type hinting to make it easier to work with.
    """

    _api_cls = CoreV1Api

    # ==== Services

    def get_namespaced_service(self, namespace: str, service_name: str) -> V1Service:
        # Typechecked wrapper
        service = self.api.read_namespaced_service(name=service_name, namespace=namespace)
        if not isinstance(service, V1Service):
            raise K8sException(
                f"Failed to retrieve Service with name: '{service_name}' in namespace: '{namespace}' "
                f"(Got obj of type: '{type(service)}')"
            )
        return service

    def get_service(self, namespace: str, service_name: str) -> Service | None:
        try:
            v1service = self.get_namespaced_service(namespace=namespace, service_name=service_name)
            if v1service is not None:
                return Service.from_model(v1service)
        except (ApiException, K8sException) as ex:
            LOG.warning(f"Error retrieving Service: {ex}")
        return None

    def list_namespaced_services(self, namespace: str) -> V1ServiceList | None:
        # Typechecked wrapper
        service_list = self.api.list_namespaced_service(namespace=namespace)
        if not isinstance(service_list, V1ServiceList):
            raise K8sException(
                f"Failed to retrieve Service list in namespace: '{namespace}' "
                f"(Got obj of type: '{type(service_list)}')"
            )
        return service_list

    def get_all_services(self, namespace: str) -> list[Service]:
        try:
            service_list = self.list_namespaced_services(namespace=namespace)
            if service_list and service_list.items is not None:
                return [Service.from_model(service) for service in service_list.items]

            LOG.warning("Retrieved empty service_list in `get_all_services()`")
        except ApiException as ex:
            LOG.warning(f"Error retrieving Services: {ex}")

        return []

    def get_services_for_ingress(self, ingress: Ingress) -> list[Service]:
        service_names = ingress.get_all_service_names()
        services = []
        for name in service_names:
            svc = self.get_service(namespace=ingress.namespace, service_name=name)
            if svc is not None:
                services.append(svc)
        return services

    # ==== Secrets

    def get_namespaced_secret(self, namespace: str, name: str) -> V1Secret:
        # Typechecked wrapper
        secret = self.api.read_namespaced_secret(name=name, namespace=namespace)
        if not isinstance(secret, V1Secret):
            raise K8sException(
                f"Failed to retrieve Secret with name: '{name}' in namespace: '{namespace}' "
                f"(Got obj of type: '{type(secret)}')"
            )
        return secret

    def get_secret(self, namespace: str, name: str) -> Secret | None:
        try:
            v1secret: V1Secret = self.get_namespaced_secret(
                namespace=namespace,
                name=name,
            )
            if v1secret is not None:
                return Secret.from_model(v1secret)
        except (ApiException, K8sException) as ex:
            LOG.warning(f"Error retrieving Secret: {ex}")
        return None

    def create_secret(self, secret: Secret):
        try:
            self.api.create_namespaced_secret(
                namespace=secret.namespace,
                body=secret.to_model(),
            )
        except (ApiException, K8sException) as ex:
            LOG.warning(f"Error creating Secret: {ex}")
        return None

    def replace_secret(self, secret: Secret):
        try:
            self.api.replace_namespaced_secret(
                name=secret.name,
                namespace=secret.namespace,
                body=secret.to_model(),
            )
        except (ApiException, K8sException) as ex:
            LOG.warning(f"Error replacing Secret: {ex}")
        return None

    def delete_secret(self, secret: Secret):
        try:
            self.api.delete_namespaced_secret(
                name=secret.name,
                namespace=secret.namespace,
            )
        except (ApiException, K8sException) as ex:
            LOG.warning(f"Error deleting Secret: {ex}")
        return None

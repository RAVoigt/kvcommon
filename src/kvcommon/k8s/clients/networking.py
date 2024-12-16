from kubernetes.client import NetworkingV1Api
from kubernetes.client.exceptions import ApiException
from kubernetes.client.models.v1_ingress import V1Ingress
from kubernetes.client.models.v1_ingress_list import V1IngressList

from kvcommon.exceptions import K8sException
from kvcommon.k8s.entities.backendconfig import BackendConfig
from kvcommon.k8s.entities.ingress import Ingress
from kvcommon.k8s.entities.service import Service

from .base import K8sClientBase
from .core import K8sCoreClient
from .custom_objects import K8sCustomObjectsClient


from kvcommon.logger import get_logger

LOG = get_logger("kvc-k8s")


class K8sNetworkingClient(K8sClientBase[NetworkingV1Api]):
    """
    The kubernetes client is maddeningly opaque when it comes to typing and return values.

    Wrap the parts of it we're using in a convenience layer with type hinting to make it easier to work with.
    """

    _api_cls = NetworkingV1Api

    def get_namespaced_ingress(self, namespace: str, ingress_name: str) -> V1Ingress:
        # Typechecked wrapper
        ingress = self.api.read_namespaced_ingress(name=ingress_name, namespace=namespace)
        if not isinstance(ingress, V1Ingress):
            raise K8sException(
                f"Failed to retrieve Ingress with name: '{ingress_name}' in namespace: '{namespace}' "
                f"(Got obj of type: '{type(ingress)}')"
            )
        return ingress

    def get_ingress(self, namespace: str, ingress_name: str) -> Ingress | None:
        try:
            v1ingress = self.get_namespaced_ingress(namespace=namespace, ingress_name=ingress_name)
            if v1ingress is not None:
                return Ingress.from_model(v1ingress)
        except (ApiException, K8sException) as ex:
            LOG.warning(f"Error retrieving Ingress: {ex}")
        return None

    def list_namespaced_ingress(self, namespace: str) -> V1IngressList:
        # Typechecked wrapper
        ingress_list = self.api.list_namespaced_ingress(namespace=namespace)
        if not isinstance(ingress_list, V1IngressList):
            raise K8sException(
                f"Failed to retrieve Ingress list in namespace: '{namespace}' "
                f"(Got obj of type: '{type(ingress_list)}')"
            )
        return ingress_list

    def get_all_ingresses(self, namespace: str) -> list[Ingress]:
        try:
            ingress_list = self.list_namespaced_ingress(namespace=namespace)
            if ingress_list and ingress_list.items is not None:
                return [Ingress.from_model(ingress) for ingress in ingress_list.items]

            LOG.warning("Retrieved empty ingress_list in `get_all_ingresses()`")
        except ApiException as ex:
            LOG.warning(f"Error retrieving Ingresses: {ex}")

        return []

    def get_backend_config(self, namespace: str, name: str) -> BackendConfig:
        """
        Uses the Custom Objects API, but adding a convenience wrapper here because it's networking-related
        """
        client = K8sCustomObjectsClient(in_cluster=self._in_cluster)
        return client.get_backend_config(namespace=namespace, name=name)

    def get_all_services(self, namespace: str) -> list[Service]:
        """
        Uses the Core API, but adding a convenience wrapper here because it's networking-related
        """
        client = K8sCoreClient(in_cluster=self._in_cluster)
        return client.get_all_services(namespace=namespace)

    def get_service(self, namespace: str, service_name: str) -> Service | None:
        """
        Uses the Core API, but adding a convenience wrapper here because it's networking-related
        """
        client = K8sCoreClient(in_cluster=self._in_cluster)
        return client.get_service(namespace=namespace, service_name=service_name)

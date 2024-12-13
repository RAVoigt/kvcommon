import kubernetes
from kubernetes.client import NetworkingV1Api
from kubernetes.client.exceptions import ApiException
from kubernetes.client.models.v1_ingress import V1Ingress
from kubernetes.client.models.v1_ingress_list import V1IngressList

from kvcommon.logger import get_logger
from . import K8sException
from . import K8sClientBase


LOG = get_logger("kvc-k8s")


class K8sNetworkingClient(K8sClientBase[NetworkingV1Api]):
    """
    The kubernetes client is maddeningly opaque when it comes to typing and return values.

    Wrap the parts of it we're using in a convenience layer with type hinting to make it easier to work with.
    """

    _api_cls: NetworkingV1Api

    def read_namespaced_ingress(self, namespace: str, ingress_name: str) -> V1Ingress:
        # Typechecked wrapper
        ingress = self._api.read_namespaced_ingress(
            name=ingress_name, namespace=namespace
        )
        if not isinstance(ingress, V1Ingress):
            raise K8sException(
                f"Failed to retrieve ingress with name: '{ingress_name} in namespace: '{namespace}' "
                f"(Got obj of type: '{type(ingress)}')"
            )
        return ingress

    def list_namespaced_ingress(self, namespace: str) -> V1IngressList:
        # Typechecked wrapper
        ingress_list = self._api.list_namespaced_ingress(namespace=namespace)
        if not isinstance(ingress_list, V1IngressList):
            raise K8sException(
                f"Failed to retrieve ingress list in namespace: '{namespace}' "
                "(Got obj of type: '{type(ingress_list)}')"
            )
        return ingress_list

    def get_ingress(self, namespace: str, ingress_name: str) -> V1Ingress | None:
        try:
            return self.read_namespaced_ingress(namespace=namespace, ingress_name=ingress_name)
        except (ApiException, K8sException) as ex:
            LOG.warning(f"Error retrieving ingress: {ex}")
            return None

    def get_all_ingresses(self, namespace: str) -> list:
        try:
            ingress_list = self.list_namespaced_ingress(namespace=namespace)
            if ingress_list and ingress_list.items is not None:
                return ingress_list.items
            LOG.warning("Retrieved empty ingress_list in `_get_ingresses()`")
            return []
        except ApiException as ex:
            LOG.warning(f"Error retrieving ingress: {ex}")
            return []

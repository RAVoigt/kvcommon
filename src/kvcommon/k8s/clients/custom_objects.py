from kubernetes.client import CustomObjectsApi
from kubernetes.client.exceptions import ApiException

from kvcommon.exceptions import K8sException
from kvcommon.k8s.entities.ingress import Ingress
from kvcommon.k8s.entities.service import Service
from kvcommon.k8s.entities.backendconfig import BackendConfig

from .base import K8sClientBase
from .core import K8sCoreClient

from kvcommon.logger import get_logger

LOG = get_logger("kvc-k8s")


class K8sCustomObjectsClient(K8sClientBase[CustomObjectsApi]):
    """
    The kubernetes client is maddeningly opaque when it comes to typing and return values.

    Wrap the parts of it we're using in a convenience layer with type hinting to make it easier to work with.
    """

    _api_cls = CustomObjectsApi

    def get_backend_config(self, namespace: str, name: str) -> BackendConfig:

        # Retrieve the BackendConfig
        try:
            backend_config = self.api.get_namespaced_custom_object(
                group="cloud.google.com",
                version="v1",
                namespace=namespace,
                plural="backendconfigs",  # Plural name of the CRD
                name=name,
            )
            if not isinstance(backend_config, dict):
                raise K8sException(
                    f"Non-dict retrieved for backendconfig with name "
                    "'{name}' in namespace: '{namespace}'"
                )
            return BackendConfig.from_dict(backend_config)
        except ApiException as ex:
            LOG.warning(f"Error retrieving BackendConfig: {ex}")
            raise

    def get_backend_configs_for_service(self, service: Service) -> set[BackendConfig]:
        backendconfigs = set()
        backendconfig_names: set = service.get_backend_config_names()

        for bec_name in backendconfig_names:
            bec = self.get_backend_config(namespace=service.namespace, name=bec_name)
            if bec is not None:
                backendconfigs.add(bec)
        return backendconfigs

    def get_backend_configs_for_ingress(self, ingress: Ingress) -> set[BackendConfig]:
        core_client = K8sCoreClient(in_cluster=self._in_cluster)
        services = core_client.get_services_for_ingress(ingress)

        backendconfigs = set()
        for svc in services:
            becs = self.get_backend_configs_for_service(svc)
            for bec in becs:
                backendconfigs.add(bec)
        return backendconfigs

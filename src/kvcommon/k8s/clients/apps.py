import datetime
import typing as t

from kubernetes.client import AppsV1Api
from kubernetes.client.exceptions import ApiException
from kubernetes.client.models.v1_deployment import V1Deployment

from kvcommon.exceptions import K8sException
from kvcommon.k8s.entities.deployment import Deployment
from .base import K8sClientBase

from kvcommon.logger import get_logger

LOG = get_logger("kvc-k8s")

# TODO: Versioning in names

class K8sAppsClient(K8sClientBase[AppsV1Api]):
    """
    The kubernetes client is maddeningly opaque when it comes to typing and return values.

    Wrap the parts of it we're using in a convenience layer with type hinting to make it easier to work with.
    """

    _api_cls = AppsV1Api

    # ==== Deployments

    def get_namespaced_deployment(self, namespace: str, name: str) -> V1Deployment:
        # Typechecked wrapper
        deployment = self.api.read_namespaced_deployment(name=name, namespace=namespace)
        if not isinstance(deployment, V1Deployment):
            raise K8sException(
                f"Failed to retrieve Deployment with name: '{name}' in namespace: '{namespace}' "
                f"(Got obj of type: '{type(deployment)}')"
            )
        return deployment

    def get_deployment(self, namespace: str, name: str) -> Deployment:
        try:
            v1deployment: V1Deployment = self.get_namespaced_deployment(
                namespace=namespace,
                name=name,
            )
            if v1deployment is not None:
                return Deployment.from_model(v1deployment)
        except (ApiException, K8sException) as ex:
            LOG.error(f"Error retrieving Deployment: {ex}")
            raise ex

    def rollout_restart_deployment(self, namespace: str, name: str):
        """
        Replicates the behaviour of `kubectl rollout restart` by similarly updating the 'restartedAt'
        annotation on the Pod Template of a Deployment
        """
        deployment = self.get_deployment(namespace=namespace, name=name)

        new_restartedAt = datetime.datetime.now(datetime.timezone.utc).isoformat()
        # Update the restartedAt annotation on the Deployment's Pod Template
        # Note: NOT on the Deployment's own annotations
        deployment.spec.template.metadata.set_annotation(
            annotation_key="kubectl.kubernetes.io/restartedAt",
            new_value=new_restartedAt
        )

        self.api.patch_namespaced_deployment(
            name=name,
            namespace=namespace,
            body=deployment.to_model(),
        )

import base64
import binascii

try:
    from kubernetes import client
    from kubernetes import config

except ImportError:
    # TODO: Improve handling of kubernetes as an optional dep
    # kubernetes = None
    # client = None
    # config = None
    pass

from kvcommon.exceptions import KVCException
from kvcommon.logger import get_logger

LOG = get_logger("kvc-k8s")


class KubernetesException(KVCException):
    pass


def get_k8s_secret(secret_name: str, namespace: str):
    """
    Returns a 'v1Secret' struct from kubernetes library

    Raises: 'KubernetesException' on failure
    """
    config.load_incluster_config()
    v1api = client.CoreV1Api()

    LOG.debug("Retrieving K8s secret '%s' in namespace '%s'", secret_name, namespace)

    v1secret = v1api.read_namespaced_secret(secret_name, namespace)
    if not v1secret or not hasattr(v1secret, "data"):
        raise KubernetesException(
            f"No secret retrieved for name: '{secret_name}' in namespace: '{namespace}'"
        )
    return v1secret


def get_secret_strings(secret) -> dict:
    """
    Get dict of b64-decoded strings from opaque K8s V1Secret data dict
    """

    # TODO: Some kind of typehinting wrapping of kubernetes lib
    if not secret or not hasattr(secret, "data"):
        raise KubernetesException(f"Invalid secret")

    secret_data: dict = secret.data
    data_dict = dict()

    for key, value in secret_data.items():
        try:
            data_dict[key] = base64.b64decode(value).decode("utf-8")
        except binascii.error as ex:  # type: ignore
            raise KubernetesException(
                f"Failed to b64decode value at key: '{key}' in data for secret with name: '{value}'.\n"
                f"base64 exception: {ex}"
            )

    return data_dict


def get_decoded_k8s_secret(secret_name: str, namespace: str) -> dict:
    """
    Gets a 'v1Secret' struct from kubernetes and decodes

    Raises: 'KubernetesException' on failure
    """
    try:
        secret = get_k8s_secret(secret_name=secret_name, namespace=namespace)
    except KubernetesException:
        # TODO
        raise

    return get_secret_strings(secret)

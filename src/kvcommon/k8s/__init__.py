from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

from kvcommon.exceptions import DependencyException
from kvcommon.exceptions import KVCException

try:
    import kubernetes

except ImportError:
    raise DependencyException("KVCommon: Must specify 'k8s' extra to use kubernetes features.")


class K8sException(KVCException):
    pass



ApiCls  = TypeVar("ApiCls")

class K8sClientBase(Generic[ApiCls]):
    _config_loaded: bool = False
    _in_cluster: bool = True
    _api_cls = None
    _api: ApiCls

    def __init__(self, in_cluster: bool = True) -> None:
        # TODO: Get _in_cluster from config
        self._in_cluster = in_cluster
        self._load_config()
        self._init_api_client()

    def _load_config(self):
        if self._in_cluster:
            kubernetes.config.load_incluster_config()
        else:
            kubernetes.config.load_kube_config()  # For local dev
        self._config_loaded = True

    @property
    def api(self) -> ApiCls:
        if not self._config_loaded:
            raise K8sException("Config not loaded for k8s client")
        return self._api

    def _init_api_client(self):
        if self._api_cls is None:
            raise K8sException("Client cls not configured with _api_cls")
        self._api = self._api_cls()

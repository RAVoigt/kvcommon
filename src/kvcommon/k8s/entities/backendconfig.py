from __future__ import annotations

import typing as t

from .base import K8sObject
from .base import K8sObjectSpec
from .serializable import K8sSerializable

from kvcommon.types import to_bool
from kvcommon.logger import get_logger

LOG = get_logger("kvc-k8s")


class Spec_BackendConfig_IAP(K8sSerializable):
    @property
    def enabled(self) -> bool:
        return to_bool(self._deserialized.get("enabled", False))

    @property
    def oauthclientCredentials(self) -> dict:
        return self._deserialized.get("oauthclientCredentials", None)

    @property
    def oauthclientCredentials_secretName(self) -> str | None:
        return self.oauthclientCredentials.get("secretName", None)


class Spec_BackendConfig_HealthCheck(K8sSerializable):
    @property
    def checkIntervalSec(self) -> int | None:
        return self._deserialized.get("checkIntervalSec", None)

    @property
    def timeoutSec(self) -> int | None:
        return self._deserialized.get("timeoutSec", None)

    @property
    def healthyThreshold(self) -> int | None:
        return self._deserialized.get("healthyThreshold", None)

    @property
    def unhealthyThreshold(self) -> int | None:
        return self._deserialized.get("unhealthyThreshold", None)

    @property
    def type(self) -> str | None:
        return self._deserialized.get("type", None)

    @property
    def requestPath(self) -> str | None:
        return self._deserialized.get("requestPath", None)

    @property
    def port(self) -> int | None:
        port = self._deserialized.get("port", None)
        if port is not None:
            return int(port)


class Spec_BackendConfig(K8sObjectSpec):
    @property
    def iap(self) -> Spec_BackendConfig_IAP:
        iap_dict = self._deserialized.get("iap", {})
        return Spec_BackendConfig_IAP.from_dict(iap_dict)

    @property
    def securityPolicy(self) -> dict | None:
        return self._deserialized.get("securityPolicy", None)

    @property
    def healthCheck(self) -> Spec_BackendConfig_HealthCheck:
        healthCheck_dict = self._deserialized.get("healthCheck", {})
        return Spec_BackendConfig_HealthCheck.from_dict(healthCheck_dict)

    @property
    def customRequestHeaders(self) -> dict | None:
        return self._deserialized.get("customRequestHeaders", None)


class BackendConfig(K8sObject):
    _expected_kind = "BackendConfig"
    _spec: Spec_BackendConfig

    def __init__(self, serialized: str, deserialized: dict) -> None:
        super().__init__(serialized, deserialized)
        self._spec = Spec_BackendConfig.from_dict(deserialized.get("spec", {}))

    @property
    def is_namespaced(self) -> bool:
        return True

    @property
    def iap(self) -> Spec_BackendConfig_IAP:
        return self._spec.iap.copy()

    @property
    def iap_enabled(self) -> bool:
        return self.iap.enabled

    @property
    def iap_secretName(self) -> str | None:
        return self.iap.oauthclientCredentials_secretName

    @property
    def securityPolicy(self) -> dict | None:
        return self._spec.securityPolicy

    @property
    def healthCheck(self) -> Spec_BackendConfig_HealthCheck:
        return self._spec.healthCheck.copy()

    @property
    def customRequestHeaders(self) -> dict | None:
        return self._spec.customRequestHeaders

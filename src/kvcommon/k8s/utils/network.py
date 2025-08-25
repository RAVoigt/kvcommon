import dataclasses
import socket
from urllib.parse import urlunparse

from kvcommon.exceptions import KVCNetworkException
from kvcommon.logger import get_logger
from kvcommon.urls import urlparse_ignore_scheme

LOG = get_logger("kvc-network")


@dataclasses.dataclass(kw_only=True)
class ReplicaRecord:
    ip: str
    port: int

    def __str__(self) -> str:
        return f"<Replica: {self.ip}:{self.port}>"

    @property
    def url(self, scheme: str = "http") -> str:
        return urlunparse((scheme, f"{self.ip}:{self.port}", "", "", "", ""))

    def __eq__(self, other):
        return isinstance(other, ReplicaRecord) and self.ip == other.ip and self.port == other.port

    def __hash__(self):
        return hash(f"{self.ip}:{self.port}")


def get_headless_service_replica_ips(service_url: str, service_port: int | str | None = None) -> set[ReplicaRecord]:
    parsed = urlparse_ignore_scheme(service_url)
    service_hostname = parsed.hostname
    service_port = service_port or parsed.port
    if not service_port:
        raise ValueError(f"service_url must include port if service_port is not provided separately: {service_url}")

    # Resolve all A records of the headless K8s service
    # LOG.debug("Querying headless K8s service for replica IPs: " + f"{service_hostname}:{service_port}")
    try:
        records_raw = socket.getaddrinfo(service_hostname, service_port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as ex:
        raise KVCNetworkException(f"Failed to resolve headless service '{service_hostname}:{service_port}': {ex}")

    records = set()
    for record in records_raw:
        records.add(ReplicaRecord(ip=str(record[4][0]), port=int(record[4][1])))

    return records

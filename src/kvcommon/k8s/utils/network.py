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


def get_all_replica_ips_from_headless_service(service_url: str, service_port: int|str|None = None) -> set[ReplicaRecord]:
    if not service_port:
        parsed = urlparse_ignore_scheme(service_url)
        service_url = f"{parsed.scheme}://{parsed.hostname}"
        service_port = parsed.port

        if not service_port:
            raise ValueError(f"service_url must include port if service_port is not provided separately: {service_url}")

    # Resolve all A records of the headless K8s service
    # LOG.debug("Querying headless K8s service for replica IPs: " + f"{service_url}:{service_port}")
    try:
        records_raw = socket.getaddrinfo(service_url, service_port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as ex:
        raise KVCNetworkException(f"Failed to resolve headless service '{service_url}:{service_port}': {ex}")

    records = set()
    for record in records_raw:
        LOG.debug(f"Resolved record: {record}")
        records.add(ReplicaRecord(ip=str(record[4][0]), port=int(record[4][1])))

    return records

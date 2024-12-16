class KVCException(Exception):
    pass


class DependencyException(KVCException):
    pass


class K8sException(KVCException):
    pass


class InvalidDataException(K8sException):
    pass


class KVCFlaskException(KVCException):
    pass

class KVCException(Exception):
    pass


class DependencyException(KVCException):
    pass


class K8sException(KVCException):
    pass


class DataIntegrityException(K8sException):
    pass


class KVCFlaskException(KVCException):
    pass


class EnvVarException(KVCException):
    pass


class EnvVarTypeException(KVCException):
    pass

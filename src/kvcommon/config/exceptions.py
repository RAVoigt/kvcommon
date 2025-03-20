from kvcommon.exceptions import KVCException


class ConfigValidationError(KVCException):
    def __init__(self, var_name: str, err: str, *args, **kwargs):
        msg = f"ConfigVar '{var_name}' failed validation for reason: '{err}'"
        super().__init__(msg, *args, **kwargs)


class ImmutableVarException(KVCException):
    def __init__(self, msg="ConfigVar is immutable", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class UnsupportedTypeException(KVCException):
    def __init__(self, attempted_type: type, *args, **kwargs):
        msg = f"Type not supported for ConfigVar: {attempted_type.__name__}; "
        super().__init__(msg, *args, **kwargs)

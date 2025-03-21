import os
from typing import Collection
from typing import Generic
from typing import Type

from kvcommon.types import to_bool

from .var import ConfigVarType
from .var import ConfigVarImmutable
from .validators import VarValidator


def os_get_env(key: str, default: str = "") -> str:
    # Typed wrapper
    if not isinstance(default, str):
        raise TypeError(
            f"os_get_env default must be of type 'str' - got: '{default}' (type: '{type(default).__name__}')"
        )
    value = os.getenv(key, default=default)
    if value is None:
        return ""
    return value


class EnvVar(Generic[ConfigVarType]):
    _name: str
    _env_var_key: str
    _coerce_type: Type[ConfigVarType]
    _var: ConfigVarImmutable

    def __init__(self, key: str, default: ConfigVarType, coerce_type: Type[ConfigVarType]) -> None:

        self._env_var_key = key
        self._coerce_type = coerce_type

        value_from_env = os_get_env(key)
        if not value_from_env:
            value_from_env = default
        else:
            if coerce_type == bool:
                value_from_env = to_bool(value_from_env)
            elif coerce_type == int:
                value_from_env = int(value_from_env)
            elif coerce_type == float:
                value_from_env = float(value_from_env)
            elif coerce_type == str:
                value_from_env = str(value_from_env)
            elif coerce_type == list:
                values = str(value_from_env).split(",")
                value_from_env = [value.strip() for value in values]

        self._var = ConfigVarImmutable(name=key, value=value_from_env, expected_type=coerce_type)

    def __str__(self) -> str:
        return str(self._var.value)

    def __repr__(self) -> str:
        return f"<EnvVar:{self._coerce_type.__name__}:{str(self._var.value)}>"

    @property
    def name(self) -> str:
        return self._var._name

    @property
    def value(self) -> ConfigVarType:
        return self._var.value

    def validate(self, validators: VarValidator | Collection[VarValidator]) -> ConfigVarType:
        return self._var.validate(validators)

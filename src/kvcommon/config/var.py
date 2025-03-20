import os
import typing as t
from typing import Collection
from typing import Generic
from typing import Type
from typing import TypeVar


from .exceptions import ImmutableVarException
from .validators import VarValidator


ConfigVarType = TypeVar("ConfigVarType", int, float, str, bool, list, dict)


class ConfigVar(Generic[ConfigVarType]):
    _name: str
    _value_type: Type[ConfigVarType]
    _value: ConfigVarType

    def __init__(
        self,
        name: str,
        value: ConfigVarType,
        expected_type: Type[ConfigVarType]
    ) -> None:

        self._name = name
        self._value_type = expected_type
        self._set(value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"<ConfigVar:{self._value_type.__name__}:{str(self._value)}>"

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> ConfigVarType:
        return self._value

    def _set(self, new_value):
        if not isinstance(new_value, self._value_type):
            raise TypeError(
                f"ConfigVar unexpected type for new_value: '{type(new_value).__name__}'"
                f" - Expected: '{self._value_type.__name__}'"
            )
        self._value = new_value

    def set(self, new_value):
        self._set(new_value)

    def validate(self, validators: VarValidator | Collection[VarValidator]) -> ConfigVarType:
        """
        Validate the value of the ConfigVar against a collection of VarValidators

        raises: `ConfigValidationError` (if validation failed)

        returns: `ConfigVar.value` (on successful validation)
        """
        if not isinstance(validators, Collection):
            validators = (validators, )
        for v in validators:
            v.set_name(self._name)
            v(self.value)
        return self.value


class ConfigVarImmutable(ConfigVar):
    _init_done: bool = False

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._init_done = True

    def __setattr__(self, name, value):
        if self._init_done:
            raise ImmutableVarException()
        super().__setattr__(name, value)

    def set(self, *args, **kwargs):
        if self._init_done:
            raise ImmutableVarException()
        super().set(*args, **kwargs)

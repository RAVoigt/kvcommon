import os
import typing as t
from typing import Collection
from typing import Generic
from typing import Type
from typing import TypeVar


from .exceptions import ImmutableVarException
from .validators import VarValidator


ConfigVarType = TypeVar("ConfigVarType", int, float, str, bool)
ConfigVarType_Complex = TypeVar("ConfigVarType_Complex", str, Collection, dict)  # TODO


class ConfigVar(Generic[ConfigVarType]):
    _name: str
    _value_type: Type[ConfigVarType]
    _value: ConfigVarType
    _validators: list[VarValidator]

    def __init__(
        self,
        name: str,
        value: ConfigVarType,
        expected_type: Type[ConfigVarType],
        validators: VarValidator | list[VarValidator] | None = None,
    ) -> None:

        self._name = name
        self._value_type = expected_type
        self._set(value)

        self._validators = list()
        if validators:
            self.add_validator(validators)

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

    def add_validator(self, new_validator: VarValidator | Collection[VarValidator]):
        if isinstance(new_validator, Collection):
            for v in new_validator:
                v.set_name(self._name)
            self._validators.extend(new_validator)
        else:
            new_validator.set_name(self._name)
            self._validators.append(new_validator)

    def validate(self):
        for validator in self._validators:
            validator(self.value)


class ConfigVarImmutable(ConfigVar):

    def __setattr__(self, name, value):
        raise ImmutableVarException()

    def set(self, *args, **kwargs):
        raise ImmutableVarException()

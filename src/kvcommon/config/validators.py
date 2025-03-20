import typing as t
from typing import Callable
from typing import Protocol

from .exceptions import ConfigValidationError


class ValidatorFunc(Protocol):
    def __call__(self, value: t.Any) -> bool: ...


ValidatorFuncType = ValidatorFunc | Callable[[t.Any,], bool,]


class VarValidator:
    _var_name: str | None
    _err_msg: str
    _validator_func: ValidatorFuncType

    def __init__(self, v_func: ValidatorFuncType, err_msg: str, var_name: str | None = None) -> None:
        if not isinstance(v_func, t.Callable):
            raise TypeError("v_func must be a callable that accepts a single param and returns bool")
        self._validator_func = v_func
        self._err_msg = err_msg
        self._var_name = var_name

    def set_name(self, var_name: str):
        self._var_name = var_name

    def __call__(self, config_var_value: t.Any) -> bool:
        result = self._validator_func(config_var_value)
        if not self._var_name:
            raise ValueError("var_name must be set for VarValidator")
        if not result:
            raise ConfigValidationError(var_name=self._var_name, err=self._err_msg)
        return True


def String_NonEmpty() -> VarValidator:
    return VarValidator(
        v_func=lambda x: isinstance(x, str) and x != "",
        err_msg="Must be a valid, non-empty string",
    )


def String_NonEmpty_NoWhitespace() -> VarValidator:
    return VarValidator(
        v_func=lambda x: isinstance(x, str) and x.strip() != "",
        err_msg="Must be a valid, non-empty, non-whitespace string",
    )


def String_NonRoot() -> VarValidator:
    return VarValidator(
        v_func=lambda x: isinstance(x, str) and x.strip() != "" and x.strip() != "/",
        err_msg="Must be a valid, non-empty string and not a 'root' path: '/'",
    )


def Number_Natural() -> VarValidator:
    return VarValidator(
        v_func=lambda x: isinstance(x, int) and x > 0,
        err_msg="Must be a natural number (int, >0)",
    )


def Number_Int_Negative() -> VarValidator:
    return VarValidator(
        v_func=lambda x: isinstance(x, int) and x < 0,
        err_msg="Must be a negative int",
    )


def Number_Float_Positive() -> VarValidator:
    return VarValidator(
        v_func=lambda x: isinstance(x, float) and x > 0,
        err_msg="Must be a positive, non-zero float",
    )


def Number_Float_Negative() -> VarValidator:
    return VarValidator(
        v_func=lambda x: isinstance(x, float) and x < 0,
        err_msg="Must be a negative, non-zero float",
    )


def List_NonEmpty() -> VarValidator:
    return VarValidator(
        v_func=lambda x: isinstance(x, list) and len(x) > 0,
        err_msg="Must be a populated (non-empty) list",
    )


def condition_list_of_valid_strings(input_data: list) -> bool:
    if not isinstance(input_data, list):
        return False
    if len(input_data) < 1:
        return False
    for elem in input_data:
        if not isinstance(elem, str):
            return False
        if elem == "":
            return False
    return True


def List_Str_NonEmpty() -> VarValidator:
    return VarValidator(
        v_func=condition_list_of_valid_strings,
        err_msg="Must be a populated (non-empty) list of valid (non-empty) strings",
    )


def Set_NonEmpty() -> VarValidator:
    return VarValidator(
        v_func=lambda x: isinstance(x, set) and len(x) > 0,
        err_msg="Must be a populated (non-empty) set",
    )


def condition_set_of_valid_strings(input_data: set) -> bool:
    if not isinstance(input_data, set):
        return False
    if len(input_data) < 1:
        return False
    for elem in input_data:
        if not isinstance(elem, str):
            return False
        if elem == "":
            return False
    return True


def Set_Str_NonEmpty() -> VarValidator:
    return VarValidator(
        v_func=condition_set_of_valid_strings,
        err_msg="Must be a populated (non-empty) set of valid (non-empty) strings",
    )

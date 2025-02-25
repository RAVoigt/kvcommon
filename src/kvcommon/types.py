import json
import typing as t


def to_bool(val: None | bool | int | float | str) -> bool:
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, int):
        if val == 0:
            return False
        return True
    if isinstance(val, float):
        if val == 0.0:
            return False
        return True
    if isinstance(val, str):
        val = val.strip().lower()
        if val == "" or val in ["false", "no", "n", "0"]:
            return False
        if val in ["true", "yes", "y", "1"]:
            return True

    raise ValueError(f"Unable to coerce value to boolean: {val}")


def is_number_natural(value: int | t.Any) -> bool:
    return isinstance(value, int) and value > 0


def is_str_nonempty(value: str | t.Any, allow_whitespace: bool = False) -> bool:
    if not isinstance(value, str):
        return False
    if not allow_whitespace:
        value = value.strip()
    return value != ""


def is_list_nonempty(value: list | t.Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def is_list_of_strings_nonempty(value: list | t.Any, allow_whitespace_strings: bool = False) -> bool:
    if not isinstance(value, list):
        return False
    if len(value) < 1:
        return False
    for elem in value:
        if not is_str_nonempty(elem, allow_whitespace=allow_whitespace_strings):
            return False
    return True


def is_json(value: t.Any, try_decode: bool = False) -> bool:
    """
    Heuristically check if a string is a JSON array or object

    Trying to loads() the string is a robust way to ensure the string is valid JSON.
    but the simple heuristic may be enough in some use cases
    """
    if not isinstance(value, str):
        return False
    value = value.strip()
    if not (value.startswith("{") or value.startswith("[")):
        return False

    if not try_decode:
        return True

    try:
        json.loads(value)
    except json.JSONDecodeError:
        return False

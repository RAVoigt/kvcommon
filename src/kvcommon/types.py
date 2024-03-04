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

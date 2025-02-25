from __future__ import annotations
import typing as t


# An alternative 'null' default to 'None', so that caller can explicitly set None as a default to return in case of missing key
class NoDefault:
    pass


NO_DEFAULT = NoDefault()


def _try_get(
    data: dict, key: str, default: t.Any = NO_DEFAULT, fail_silently: bool = False
) -> t.Any | dict:
    try:
        data[key]
    except KeyError:
        if default != NO_DEFAULT:
            return default

        if fail_silently:
            pass
        else:
            # TODO
            raise


def get_nested_value(
    data: dict, nested_key_path: str, default: t.Any = NO_DEFAULT, fail_silently: bool = False
) -> t.Any:
    path_segments: list[str] = nested_key_path.split(".")
    if len(path_segments) < 1:
        raise KeyError(
            f"Invalid dict key 'path': {nested_key_path} - "
            "Must be keys separated by dots - e.g.; 'key1.key2.key3'"
        )

    num_segments = len(path_segments)
    num_retrieved = 0
    search_dict = data
    for path in path_segments:
        num_retrieved += 1
        try:
            # Only pass default through on last segment
            if num_retrieved >= num_segments and default != NO_DEFAULT:
                found = _try_get(
                    search_dict, path, default=default, fail_silently=fail_silently
                )
            else:
                found = _try_get(search_dict, path, fail_silently=fail_silently)

        except KeyError:
            if fail_silently:
                return None
            else:
                # TODO
                raise

        if num_retrieved >= num_segments:
            return found

        if isinstance(found, dict):
            search_dict = found
            continue

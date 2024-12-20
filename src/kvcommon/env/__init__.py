from __future__ import annotations
import enum
import json
import os
import typing as t

from kvcommon.exceptions import EnvVarException
from kvcommon.exceptions import EnvVarTypeException
from kvcommon.logger import get_logger
from kvcommon.types import to_bool


LOG = get_logger("needle-proxy")


class EnvironmentVars:

    class DuplicateStrategy(enum.StrEnum):
        RAISE = "raise"
        ALWAYS_LIST = "always_list"
        MERGE_LIST = "merge_list"
        OVERWRITE = "overwrite"

    @staticmethod
    def get(
        key: str, default: t.Any, expected_type: type, should_raise: bool = True
    ) -> t.Any:
        value = os.getenv(key, default)
        if not isinstance(value, expected_type) and should_raise:
            raise EnvVarTypeException(
                f"Error retrieving env var with key: '{key}' - "
                f"Expected type: '{expected_type}', Retrieved type: '{type(value)}'"
            )
        return value

    @staticmethod
    def get_str(key: str, default: str = "", should_raise: bool = True) -> str:
        return EnvironmentVars.get(
            key, default, expected_type=str, should_raise=should_raise
        )

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        raw_value = EnvironmentVars.get(key, default, expected_type=str, should_raise=False)
        return to_bool(raw_value)

    @staticmethod
    def get_list_str(
        key: str, delimiter: str = ",", default="", should_raise: bool = True
    ) -> list[str]:
        value = EnvironmentVars.get(
            key, default, expected_type=str, should_raise=should_raise
        )
        return value.split(delimiter)

    @staticmethod
    def get_json(
        key: str, default="{}", should_raise: bool = True
    ) -> dict[str, t.Any]:
        raw_value = EnvironmentVars.get(
            key, default, expected_type=str, should_raise=should_raise
        )
        try:
            return json.loads(raw_value)
        except json.JSONDecodeError as ex:
            LOG.error("Error loading JSON for env var: '%s', exception: %s", key, str(ex))
            if should_raise:
                raise
            else:
                return dict()

    @staticmethod
    def get_dict_str(
        key: str,
        delimiter: str = ",",
        key_value_delimiter: str = "/",
        default="",
        should_raise: bool = True,
        duplicate_strategy: DuplicateStrategy | str = DuplicateStrategy.ALWAYS_LIST,
    ) -> dict[str, list[str]]:
        """
        Alternative to JSON: character-separated strings split by an additional delimiter
        e.g.; "my_namespace/my_object,another_namespace/my_object,third_namespace/an_object"
        """
        raw_value = EnvironmentVars.get(
            key, default, expected_type=str, should_raise=should_raise
        )
        values = raw_value.split(delimiter)

        key_values = dict()
        for entry in values:
            parts = entry.split(key_value_delimiter)
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid entry: '{entry}' for {key}; "
                    f"Each entry must be in form 'key{key_value_delimiter}value'; "
                    f"with entries separated by: '{delimiter}'"
                )
            entry_key = parts[0]
            entry_value = parts[1]

            if entry_key in key_values:
                if duplicate_strategy == EnvironmentVars.DuplicateStrategy.RAISE:
                    raise EnvVarException(f"Duplicate key ({entry_key}) in env var: '{key}")
                elif duplicate_strategy == EnvironmentVars.DuplicateStrategy.MERGE_LIST:
                    existing_value = key_values[entry_key]
                    if isinstance(existing_value, list):
                        key_values[entry_key].append(entry_value)
                    else:
                        key_values[entry_key] = [existing_value, entry_value]

                elif duplicate_strategy == EnvironmentVars.DuplicateStrategy.OVERWRITE:
                    key_values[entry_key] = entry_value
                else:
                    err_msg = f"Invalid duplicate_strategy: {duplicate_strategy}"
                    LOG.error(err_msg)
                    if should_raise:
                        raise EnvVarException(err_msg)
            else:
                if duplicate_strategy == EnvironmentVars.DuplicateStrategy.ALWAYS_LIST:
                    key_values[entry_key] = [
                        entry_value,
                    ]
                else:
                    key_values[entry_key] = entry_value

        return key_values

    @staticmethod
    def get_int(key: str, default=None, should_raise: bool = True) -> str:
        return EnvironmentVars.get(
            key, default, expected_type=int, should_raise=should_raise
        )

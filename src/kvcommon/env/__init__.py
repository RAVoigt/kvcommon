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

    @staticmethod
    def get_env_var(
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
    def get_env_var_str(key: str, default: str = "", should_raise: bool = True) -> str:
        return EnvironmentVars.get_env_var(
            key, default, expected_type=str, should_raise=should_raise
        )

    @staticmethod
    def get_env_var_bool(key: str, default: bool = False) -> bool:
        raw_value = EnvironmentVars.get_env_var(key, default, expected_type=str, should_raise=False)
        return to_bool(raw_value)

    @staticmethod
    def get_env_var_list_str(
        key: str, delimiter: str = ",", default="", should_raise: bool = True
    ) -> list[str]:
        value = EnvironmentVars.get_env_var(
            key, default, expected_type=str, should_raise=should_raise
        )
        return value.split(delimiter)

    @staticmethod
    def get_env_var_dict_json(
        key: str, default="{}", should_raise: bool = True
    ) -> dict[str, t.Any]:
        raw_value = EnvironmentVars.get_env_var(
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
    def get_env_var_int(key: str, default=None, should_raise: bool = True) -> str:
        return EnvironmentVars.get_env_var(
            key, default, expected_type=int, should_raise=should_raise
        )

import pytest

from kvcommon.config.exceptions import ConfigValidationError
from kvcommon.config.validators import VarValidator
from kvcommon.config.var import ConfigVar


def null_func(x):
    return True

def create_fake_var(name="FakeConfigVar", value="test", expected_type=str):
    return ConfigVar(name=name, value=value, expected_type=expected_type)


def test_initialization_with_name():
    validator = VarValidator(
        v_func=lambda x: isinstance(x, str) and x != "",
        err_msg="Must be a valid, non-empty string",
        var_name="test_var",
    )
    assert validator._var_name == "test_var"
    assert validator._err_msg == "Must be a valid, non-empty string"


def test_initialization_without_name():
    validator = VarValidator(
        v_func=null_func,
        err_msg="Null"
    )
    assert validator._var_name is None
    assert validator._err_msg == "Null"


def test_call_with_valid_value():
    validator = VarValidator(
        v_func=lambda x: isinstance(x, str) and x != "",
        err_msg="Must be a valid, non-empty string",
        var_name="test_var",
    )
    result = validator("hello")
    assert result is True


def test_call_with_invalid_value():
    validator = VarValidator(
        v_func=lambda x: isinstance(x, str) and x != "",
        err_msg="Must be a valid, non-empty string",
        var_name="test_var",
    )
    with pytest.raises(ConfigValidationError) as context:
        validator("")
    assert str(context.value) == "ConfigVar 'test_var' failed validation for reason: 'Must be a valid, non-empty string'"


def test_set_name():
    validator = VarValidator(
        v_func=null_func,
        err_msg="Null"
    )
    validator.set_name("new_var_name")
    assert validator._var_name == "new_var_name"

def test_adding_to_var_sets_name():
    validator = VarValidator(
        v_func=null_func,
        err_msg="Null"
    )
    test_name = "test_adding_to_var_sets_name"
    fake_var = create_fake_var(name=test_name)
    fake_var.add_validator(validator)
    assert validator._var_name == test_name


def test_type_error_for_invalid_validator_func():
    with pytest.raises(TypeError):
        VarValidator(
            v_func="invalid function", # type: ignore
            err_msg="Null"
        )

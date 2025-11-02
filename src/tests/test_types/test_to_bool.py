import pytest
from kvcommon.types import to_bool


def test_to_bool_none():
    assert to_bool(None) == False


def test_to_bool_boolean():
    assert to_bool(True) == True
    assert to_bool(False) == False


def test_to_bool_integer():
    assert to_bool(1) == True
    assert to_bool(0) == False
    assert to_bool(-1) == True
    assert to_bool(100) == True


def test_to_bool_float():
    assert to_bool(1.0) == True
    assert to_bool(0.0) == False
    assert to_bool(-1.0) == True
    assert to_bool(0.5) == True


def test_to_bool_string_true_values():
    assert to_bool("true") == True
    assert to_bool("True") == True
    assert to_bool("trUe") == True
    assert to_bool(" yes ") == True
    assert to_bool("Y") == True
    assert to_bool("y") == True
    assert to_bool("1") == True


def test_to_bool_string_false_values():
    assert to_bool("false") == False
    assert to_bool("False") == False
    assert to_bool("falSe") == False
    assert to_bool(" no ") == False
    assert to_bool("N") == False
    assert to_bool("n") == False
    assert to_bool("0") == False
    assert to_bool("") == False
    assert to_bool("   ") == False


def test_to_bool_invalid_string():
    with pytest.raises(ValueError) as exc_info:
        to_bool("invalid")
    assert str(exc_info.value) == "Unable to coerce value to boolean: invalid"

    with pytest.raises(ValueError) as exc_info:
        to_bool("maybe")
    assert str(exc_info.value) == "Unable to coerce value to boolean: maybe"


def test_to_bool_invalid_type():
    with pytest.raises(ValueError) as exc_info:
        to_bool([1, 2, 3])  # type: ignore
    assert str(exc_info.value) == "Unable to coerce value to boolean: [1, 2, 3]"

    with pytest.raises(ValueError) as exc_info:
        to_bool({"key": "value"})  # type: ignore
    assert str(exc_info.value) == "Unable to coerce value to boolean: {'key': 'value'}"

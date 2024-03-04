import pytest
from kvcommon.types import to_bool


def test_none_returns_false():
    result = to_bool(None)
    assert result is False


def test_bool_returns_itself():
    result = to_bool(True)
    assert result is True


def test_zero_int_returns_false():
    result = to_bool(0)
    assert result is False


def test_nonzero_int_returns_true():
    result = to_bool(42)
    assert result is True


def test_zero_float_returns_false():
    result = to_bool(0.0)
    assert result is False


def test_nonzero_float_returns_true():
    result = to_bool(0.1)
    assert result is True


def test_true_string_returns_true():
    result = to_bool("true")
    assert result is True


def test_true_string_case_insensitive_returns_true():
    result = to_bool("True")
    assert result is True


def test_yes_string_returns_true():
    result = to_bool("yes")
    assert result is True


def test_yes_string_case_insensitive_returns_true():
    result = to_bool("YES")
    assert result is True


def test_y_string_returns_true():
    result = to_bool("y")
    assert result is True


def test_y_string_case_insensitive_returns_true():
    result = to_bool("Y")
    assert result is True


def test_one_string_returns_true():
    result = to_bool("1")
    assert result is True


def test_false_string_returns_false():
    result = to_bool("false")
    assert result is False


def test_false_string_case_insensitive_returns_false():
    result = to_bool("False")
    assert result is False


def test_no_string_returns_false():
    result = to_bool("no")
    assert result is False


def test_no_string_case_insensitive_returns_false():
    result = to_bool("NO")
    assert result is False


def test_n_string_returns_false():
    result = to_bool("n")
    assert result is False


def test_n_string_case_insensitive_returns_false():
    result = to_bool("N")
    assert result is False


def test_zero_string_returns_false():
    result = to_bool("0")
    assert result is False


def test_empty_string_returns_false():
    result = to_bool("")
    assert result is False


def test_whitespace_string_returns_false():
    result = to_bool("   ")
    assert result is False


def test_invalid_string_raises_value_error():
    with pytest.raises(ValueError):
        to_bool("f")


def test_unsupported_type_raises_value_error():
    with pytest.raises(ValueError):
        to_bool(print)  # type: ignore

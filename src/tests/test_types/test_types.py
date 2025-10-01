import pytest

from kvcommon.types import to_bool
from kvcommon.types import is_number_natural
from kvcommon.types import is_str_nonempty
from kvcommon.types import is_list_nonempty
from kvcommon.types import is_list_of_strings_nonempty
from kvcommon.types import is_json

from kvcommon.config.exceptions import ConfigValidationError
from kvcommon.config.validators import List_NonEmpty
from kvcommon.config.validators import List_Str_NonEmpty
from kvcommon.config.validators import Set_NonEmpty
from kvcommon.config.validators import Set_Str_NonEmpty

# ================================

class Test_ToBool:

    def test_none(self):
        assert to_bool(None) is False

    def test_bool(self):
        assert to_bool(True) is True
        assert to_bool(False) is False

    def test_int(self):
        assert to_bool(0) is False
        assert to_bool(1) is True
        assert to_bool(2) is True
        assert to_bool(-1) is True

    def test_float(self):
        assert to_bool(0.0) is False
        assert to_bool(1.0) is True
        assert to_bool(2.0) is True
        assert to_bool(0.1) is True
        assert to_bool(-0.1) is True
        assert to_bool(-1.0) is True

    def test_string(self):

        assert to_bool("True") is True
        assert to_bool("true") is True
        assert to_bool("TRUE") is True
        assert to_bool("Yes") is True
        assert to_bool("yes") is True
        assert to_bool("YES") is True
        assert to_bool("y") is True
        assert to_bool("Y") is True
        assert to_bool("1") is True

        assert to_bool("False") is False
        assert to_bool("false") is False
        assert to_bool("FALSE") is False
        assert to_bool("No") is False
        assert to_bool("no") is False
        assert to_bool("NO") is False
        assert to_bool("N") is False
        assert to_bool("n") is False
        assert to_bool("0") is False

        with pytest.raises(ValueError) as context:
            assert to_bool("2")
        with pytest.raises(ValueError) as context:
            assert to_bool("maybe")

# ================================

class Test_Is:

    def test_is_number_natural(self):
        assert is_number_natural(1.0) is False
        assert is_number_natural(1.1) is False
        assert is_number_natural(-1.0) is False
        assert is_number_natural(-1.1) is False

        assert is_number_natural(-2) is False
        assert is_number_natural(-1) is False

        assert is_number_natural(0) is False
        assert is_number_natural(1) is True
        assert is_number_natural(2) is True

        assert is_number_natural("2") is False

    def test_is_str_nonempty(self):
        assert is_str_nonempty("test", allow_whitespace=True) is True
        assert is_str_nonempty("test", allow_whitespace=False) is True
        assert is_str_nonempty("", allow_whitespace=True) is False
        assert is_str_nonempty("", allow_whitespace=False) is False
        assert is_str_nonempty(0, allow_whitespace=False) is False
        assert is_str_nonempty(1, allow_whitespace=False) is False
        assert is_str_nonempty(b"test", allow_whitespace=False) is False
        assert is_str_nonempty(b"", allow_whitespace=False) is False

        assert is_str_nonempty(" ", allow_whitespace=True) is True
        assert is_str_nonempty("one two", allow_whitespace=True) is True
        assert is_str_nonempty("one two", allow_whitespace=False) is True
        assert is_str_nonempty(" ", allow_whitespace=False) is False
        assert is_str_nonempty(" ", allow_whitespace=False) is False

    def test_is_list_nonempty(self):
        # TODO
        pass

    def test_is_list_of_strings_nonempty(self):
        # TODO
        pass

    def test_is_json(self):
        # TODO
        assert is_json(1) is False
        assert is_json("1") is False
        assert is_json("{", try_decode=True) is False

import pytest

from kvcommon.config.exceptions import ConfigValidationError
from kvcommon.config.validators import String_NonEmpty
from kvcommon.config.validators import String_NonEmpty_NoWhitespace
from kvcommon.config.validators import String_NonRoot

from . import BaseValidatorTestSuite

# ================================

class Test_String_NonEmpty(BaseValidatorTestSuite):
    validator = String_NonEmpty()

    def test_empty_string_validation(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator("")
        assert self.validator._err_msg in str(context.value)


    def test_non_string_validation(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(123)
        assert self.validator._err_msg in str(context.value)


    def test_non_empty_string_validation(self):
        result = self.validator("valid string")
        assert result is True


    def test_allows_whitespace(self):
        result = self.validator(" ")
        assert result is True

# ================================

class Test_String_NonEmpty_NoWhitespace(BaseValidatorTestSuite):
    validator = String_NonEmpty_NoWhitespace()


    def test_empty_string_validation(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator("")
        assert self.validator._err_msg in str(context.value)


    def test_non_string_validation(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(123)
        assert self.validator._err_msg in str(context.value)


    def test_non_empty_string_validation(self):
        result = self.validator("valid string")
        assert result is True


    def test_disallows_whitespace(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(" ")
        assert self.validator._err_msg in str(context.value)

# ================================

class Test_String_NonRoot(BaseValidatorTestSuite):
    validator = String_NonRoot()

    def test_empty_string_validation(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator("")
        assert self.validator._err_msg in str(context.value)


    def test_non_string_validation(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(123)
        assert self.validator._err_msg in str(context.value)


    def test_non_empty_string_validation(self):
        result = self.validator("valid string")
        assert result is True


    def test_disallows_whitespace(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(" ")
        assert self.validator._err_msg in str(context.value)


    def test_disallows_root(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator("/")
        assert self.validator._err_msg in str(context.value)

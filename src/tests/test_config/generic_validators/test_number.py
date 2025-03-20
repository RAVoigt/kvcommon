import pytest

from kvcommon.config.exceptions import ConfigValidationError
from kvcommon.config.validators import Number_Natural
from kvcommon.config.validators import Number_Int_Negative
from kvcommon.config.validators import Number_Float_Positive
from kvcommon.config.validators import Number_Float_Negative

from . import BaseValidatorTestSuite

# ================================

class Test_Number_Natural(BaseValidatorTestSuite):
    validator = Number_Natural()

    def test_empty_string_validation(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator("")
        assert self.validator._err_msg in str(context.value)

    def test_invalid(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(-3)
        assert self.validator._err_msg in str(context.value)

    def test_valid(self):
        result = self.validator(3)
        assert result is True

    def test_disallows_zero(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(0)
        assert self.validator._err_msg in str(context.value)

# ================================

class Test_Number_Int_Negative(BaseValidatorTestSuite):
    validator = Number_Int_Negative()

    def test_empty_string_validation(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator("")
        assert self.validator._err_msg in str(context.value)


    def test_invalid(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(3)
        assert self.validator._err_msg in str(context.value)

    def test_valid(self):
        result = self.validator(-3)
        assert result is True

    def test_disallows_zero(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(0)
        assert self.validator._err_msg in str(context.value)

# ================================

class Test_Number_Float_Positive(BaseValidatorTestSuite):
    validator = Number_Float_Positive()

    def test_empty_string_validation(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator("")
        assert self.validator._err_msg in str(context.value)

    def test_invalid(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(-3.0)
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator(-5)
        assert self.validator._err_msg in str(context.value)

    def test_valid(self):
        result = self.validator(3.0)
        assert result is True
        result = self.validator(0.34568)
        assert result is True

    def test_disallows_zero(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(0)
        assert self.validator._err_msg in str(context.value)

# ================================

class Test_Number_Float_Negative(BaseValidatorTestSuite):
    validator = Number_Float_Negative()

    def test_empty_string_validation(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator("")
        assert self.validator._err_msg in str(context.value)

    def test_invalid(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(3.0)
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator(5)
        assert self.validator._err_msg in str(context.value)

    def test_valid(self):
        result = self.validator(-3.0)
        assert result is True
        result = self.validator(-0.34568)
        assert result is True

    def test_disallows_zero(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(0)
        assert self.validator._err_msg in str(context.value)

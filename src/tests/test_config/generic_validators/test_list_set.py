import pytest

from kvcommon.config.exceptions import ConfigValidationError
from kvcommon.config.validators import List_NonEmpty
from kvcommon.config.validators import List_Str_NonEmpty
from kvcommon.config.validators import Set_NonEmpty
from kvcommon.config.validators import Set_Str_NonEmpty

from . import BaseValidatorTestSuite

# ================================

class Test_List_NonEmpty(BaseValidatorTestSuite):
    validator = List_NonEmpty()

    def test_valid(self):
        result = self.validator([1,])
        assert result is True
        result = self.validator([1,2])
        assert result is True

    def test_invalid(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator([])
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator("")
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator(3)
        assert self.validator._err_msg in str(context.value)

    def test_disallows_set(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(set([1,2]))
        assert self.validator._err_msg in str(context.value)

# ================================

class Test_List_Str_NonEmpty(BaseValidatorTestSuite):
    validator = List_Str_NonEmpty()

    def test_valid(self):
        result = self.validator(["1",])
        assert result is True
        result = self.validator(["1","2"])
        assert result is True

    def test_invalid(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator([])
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator("")
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator([""])
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator(["1", ""])
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator(3)
        assert self.validator._err_msg in str(context.value)

    def test_disallows_set(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(set(["1","2"]))
        assert self.validator._err_msg in str(context.value)

# ================================

class Test_Set_NonEmpty(BaseValidatorTestSuite):
    validator = Set_NonEmpty()

    def test_valid(self):
        result = self.validator({1,})
        assert result is True
        result = self.validator({1,2,1})
        assert result is True

    def test_invalid(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator({})
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator("")
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator(3)
        assert self.validator._err_msg in str(context.value)

    def test_disallows_list(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(list({"1","2"}))
        assert self.validator._err_msg in str(context.value)

# ================================

class Test_Set_Str_NonEmpty(BaseValidatorTestSuite):
    validator = Set_Str_NonEmpty()

    def test_valid(self):
        result = self.validator({"1",})
        assert result is True
        result = self.validator({"1","2","1"})
        assert result is True

    def test_invalid(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator({})
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator("")
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator({""})
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator({"1", ""})
        assert self.validator._err_msg in str(context.value)

        with pytest.raises(ConfigValidationError) as context:
            self.validator(3)
        assert self.validator._err_msg in str(context.value)

    def test_disallows_list(self):
        with pytest.raises(ConfigValidationError) as context:
            self.validator(list({"1","2"}))
        assert self.validator._err_msg in str(context.value)

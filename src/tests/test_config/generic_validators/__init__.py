import typing
from unittest import TestCase

from kvcommon.config.validators import VarValidator
from kvcommon.config.var import ConfigVar


def null_func(x):
    return True


def create_fake_var(name="FakeConfigVar", value=3, expected_type=int):
    return ConfigVar(name=name, value=value, expected_type=expected_type)


class BaseValidatorTestSuite(TestCase):

    validator: VarValidator

    def setUp(self) -> None:
        self.var: ConfigVar = create_fake_var()
        self.validator.set_name(self.var.name)
        return super().setUp()

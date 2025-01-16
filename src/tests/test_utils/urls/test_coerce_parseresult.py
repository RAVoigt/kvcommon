import pytest

from urllib.parse import urlparse
from urllib.parse import ParseResult
from kvcommon.urls import coerce_parseresult


def test_str():
    value = "https://www.example.com"
    result = coerce_parseresult(value)
    assert isinstance(result, ParseResult)

def test_parseresult():
    value = urlparse("https://www.example.com")
    result = coerce_parseresult(value)
    assert isinstance(result, ParseResult)

def test_invalid():
    value = 1
    with pytest.raises(TypeError):
        result = coerce_parseresult(value)
    value = True
    with pytest.raises(TypeError):
        result = coerce_parseresult(value)
    value = dict()
    with pytest.raises(TypeError):
        result = coerce_parseresult(value)

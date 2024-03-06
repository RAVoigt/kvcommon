import pytest
from urllib.parse import ParseResult
from kvcommon.urls import get_netloc_without_port_from_url_parts


def test_get_netloc_without_port():
    url_parts_with_port = ParseResult(
        scheme="https",
        netloc="example.com",
        path="/path/to/resource",
        params="",
        query="",
        fragment="",
    )
    netloc_without_port = get_netloc_without_port_from_url_parts(url_parts_with_port)
    assert netloc_without_port == "example.com"


def test_get_netloc_without_port_no_port():
    url_parts_without_port = ParseResult(
        scheme="https",
        netloc="example.com",
        path="/path/to/resource",
        params="",
        query="",
        fragment="",
    )
    netloc_without_port = get_netloc_without_port_from_url_parts(url_parts_without_port)
    assert netloc_without_port == "example.com"


def test_get_netloc_without_port_empty_netloc():
    url_parts_empty_netloc = ParseResult(
        scheme="https", netloc="", path="/path/to/resource", params="", query="", fragment=""
    )
    netloc_without_port = get_netloc_without_port_from_url_parts(url_parts_empty_netloc)
    assert netloc_without_port == ""

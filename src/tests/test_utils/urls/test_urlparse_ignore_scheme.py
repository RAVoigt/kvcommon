from urllib.parse import urlparse
from urllib.parse import ParseResult
from kvcommon.urls import urlparse_ignore_scheme

DEFAULT_EXPECTED_NETLOC = "example.com"
DEFAULT_EXPECTED_PATH = "/path/to/resource"
DEFAULT_EXPECTED_URL = f"{DEFAULT_EXPECTED_NETLOC}{DEFAULT_EXPECTED_PATH}"


def assert_parse_result_equal(
    result,
    scheme,
    netloc=DEFAULT_EXPECTED_NETLOC,
    path=DEFAULT_EXPECTED_PATH,
    params="",
    query="",
    fragment="",
):
    assert result.scheme == scheme
    assert result.netloc == netloc
    assert result.path == path
    assert result.params == params
    assert result.query == query
    assert result.fragment == fragment


def test_valid_url_without_scheme_force_scheme_true():
    url = DEFAULT_EXPECTED_URL
    result = urlparse_ignore_scheme(url, force_scheme=True)
    assert_parse_result_equal(result, scheme="http")


def test_valid_url_without_scheme_force_scheme_false():
    url = DEFAULT_EXPECTED_URL
    result = urlparse_ignore_scheme(url, force_scheme=False)
    assert_parse_result_equal(result, scheme="")


def test_valid_url_with_scheme_http():
    url = f"http://{DEFAULT_EXPECTED_URL}"
    result = urlparse_ignore_scheme(url)
    assert_parse_result_equal(result, scheme="http")


def test_valid_url_with_scheme_https():
    url = f"https://{DEFAULT_EXPECTED_URL}"
    result = urlparse_ignore_scheme(url, scheme="https")
    assert_parse_result_equal(result, scheme="https")


def test_custom_scheme():
    url = f"ftp://{DEFAULT_EXPECTED_URL}"
    custom_scheme = "ftp"
    result = urlparse_ignore_scheme(url, scheme=custom_scheme)
    assert_parse_result_equal(result, scheme=custom_scheme)


def test_empty_url():
    url = ""
    result = urlparse_ignore_scheme(url)
    assert_parse_result_equal(result, scheme="", netloc="", path="")


def test_url_with_params():
    url = f"{DEFAULT_EXPECTED_URL};param=value"
    result = urlparse_ignore_scheme(url)
    assert_parse_result_equal(result, scheme="", params="param=value")


def test_url_with_query():
    url = f"{DEFAULT_EXPECTED_URL}?query=value"
    result = urlparse_ignore_scheme(url)
    assert_parse_result_equal(result, scheme="", query="query=value")


def test_url_with_fragment():
    url = f"{DEFAULT_EXPECTED_URL}#fragment"
    result = urlparse_ignore_scheme(url)
    assert_parse_result_equal(result, scheme="", fragment="fragment")


def test_url_with_username_password():
    url = f"user:pass@{DEFAULT_EXPECTED_URL}"
    result = urlparse_ignore_scheme(url)
    assert result.username == "user"
    assert result.password == "pass"
    assert_parse_result_equal(result, scheme="", netloc=f"user:pass@{DEFAULT_EXPECTED_NETLOC}")

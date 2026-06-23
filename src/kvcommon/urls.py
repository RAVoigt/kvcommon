import typing as t
from urllib.parse import urlparse
from urllib.parse import ParseResult
from urllib.parse import quote


def urlparse_ignore_scheme(
    url: str, scheme: str = "http", force_scheme: bool = False
) -> ParseResult:
    """This function performs urllib.parse.urlparse on a URL string while ignoring its scheme.

    This allows for calling urlparse on a URL that is lacking a scheme (e.g. to extract the netloc),
    or with an alternate scheme.
    This function sets a scheme if one is specified or absent, to satisfy urlparse's expectations.

    Args:
        scheme: Scheme to use for urlparse. Defaults to "http"
        force_scheme: Ensures the scheme parsed-against is returned in the ParseResult, else "" is returned for scheme
    """

    if not scheme:
        scheme = "http"

    url_parts = None
    no_input_scheme = False

    if url.startswith("://"):
        url = f"{scheme}://{url[3:]}"
        no_input_scheme = True

    if "://" not in url[0:12]:
        url = f"{scheme}://{url}"
        no_input_scheme = True

    url_parts = urlparse(url)

    # Return new ParseResult with blanked scheme since we faked it only for the purposes of making urlparse work
    out_scheme = url_parts.scheme
    if no_input_scheme:
        out_scheme = ""
        if force_scheme:
            out_scheme = scheme

    return ParseResult(
        out_scheme,
        url_parts.netloc,
        url_parts.path,
        url_parts.params,
        url_parts.query,
        url_parts.fragment,
    )


def coerce_parseresult(url: str | ParseResult, ignore_scheme: bool = False) -> ParseResult:
    if isinstance(url, ParseResult):
        return url
    if isinstance(url, str):
        if ignore_scheme:
            return urlparse_ignore_scheme(url)
        return urlparse(url)
    raise TypeError("url must be str or ParseResult")


def get_netloc_without_port_from_url_parts(url_parts: ParseResult) -> str:
    # urlparse sadly doesn't provide an easy way to remove/replace the port in netloc
    netloc = url_parts.netloc
    port_str = ":%s" % url_parts.port
    if netloc.endswith(port_str):
        netloc = netloc[: len(netloc) - len(port_str)]
    return netloc


def asgi_scope_to_parse_result(scope) -> ParseResult:
    scheme = scope.get("scheme", "http")
    headers = dict(scope.get("headers", []))

    # Netloc (host:port)
    if b"host" in headers:
        netloc = headers[b"host"].decode("latin-1")
    else:
        server = scope.get("server")
        if server:
            host, port = server
            if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
                netloc = host
            else:
                netloc = f"{host}:{port}"
        else:
            netloc = "localhost"

    # Path
    path = scope.get("root_path", "") + scope.get("path", "")
    path = quote(path)

    params = ""

    query = scope.get("query_string", b"").decode("utf-8")

    # Fragment (ASGI servers strip fragments before hitting the app, always empty)
    fragment = ""

    return ParseResult(scheme, netloc, path, params, query, fragment)

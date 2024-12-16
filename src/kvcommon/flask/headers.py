def headers_dict_to_flask_headers(headers: dict) -> list:
    """
    The requests lib typically handles headers in a dict-like structure.
    Flask expects a list of (key, value) tuples.

    Returns:
        Headers as a list of key-value tuples
    """
    return [(k, v) for k, v in headers.items()]

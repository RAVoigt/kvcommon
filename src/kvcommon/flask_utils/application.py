from __future__ import annotations

import typing as t

from flask import Flask

# from flask_cors import CORS # TODO
from flask_http_middleware import MiddlewareManager

from flask_http_middleware import BaseHTTPMiddleware
from kvcommon.flask_utils.middleware import KVCFlaskMiddleware


def create_app_with_middleware(
    middleware: BaseHTTPMiddleware | KVCFlaskMiddleware | None = None,
    flask_secret_key: str | None = None,
) -> Flask:
    flask_app = Flask(__name__)

    if middleware is not None:
        flask_app.wsgi_app = MiddlewareManager(flask_app)
        flask_app.wsgi_app.add_middleware(middleware)

    if flask_secret_key:
        flask_app.secret_key = flask_secret_key

    return flask_app

# coding=utf-8
from __future__ import annotations

import typing as t

from flask import Flask
from flask_http_middleware import BaseHTTPMiddleware
from flask_http_middleware import MiddlewareManager

from kvcommon.logger import get_logger
from kvcommon.flask.middleware import KVCFlaskMiddleware
from kvcommon.flask.views import BlueprintsDict
from kvcommon.flask.views.meta import generate_meta_view
from kvcommon.flask.views.meta import MetaBlueprintConfig


LOG = get_logger("needle-proxy")


MiddlewareType = t.TypeVar("MiddlewareType", BaseHTTPMiddleware, KVCFlaskMiddleware)


def create_app_with_middleware(
    name: str,
    middleware: MiddlewareType | None = None,
    flask_app_cls: t.Type[Flask] = Flask,
    flask_secret_key: str | None = None,
    blueprints: BlueprintsDict | None = None,
    init_callback: t.Callable[[Flask], None] | None = None,
    disable_meta_view: bool = False,
    meta_view_config: MetaBlueprintConfig | None = None,
) -> FlaskType:
    flask_app = flask_app_cls(name)

    if middleware is not None:
        flask_app.wsgi_app = MiddlewareManager(flask_app)
        flask_app.wsgi_app.add_middleware(middleware)

    if flask_secret_key:
        flask_app.secret_key = flask_secret_key

    if not disable_meta_view:
        meta_bp = generate_meta_view(meta_view_config or MetaBlueprintConfig())
        if blueprints is None:
            blueprints = BlueprintsDict()
        blueprints["meta"] = meta_bp

    if blueprints is not None:
        for prefix, blueprint in blueprints.items():
            flask_app.register_blueprint(blueprint, url_prefix=f"/{prefix}")

    if init_callback is not None:
        init_callback(flask_app)

    return flask_app

from __future__ import annotations
from dataclasses import dataclass
import typing as t

from flask import Blueprint
from flask import request
from flask.wrappers import Response as Flask_Response

from kvcommon.flask.views import get_url_map
from kvcommon.flask.responses import HTTPResponse
from kvcommon.flask.responses import HealthzAliveResponse
from kvcommon.flask.responses import HealthzNOTAliveResponse
from kvcommon.flask.responses import HealthzReadyResponse
from kvcommon.flask.responses import HealthzNOTReadyResponse


from kvcommon.logger import get_logger

LOG = get_logger("needle-proxy")


default_meta_blueprint = Blueprint("meta", __name__, url_prefix=f"/meta")


# Liveness/Readiness endpoints
@default_meta_blueprint.route("/healthz", methods=["GET"])
def healthz():
    if "ready" in request.args:
        # TODO: Readiness logic
        return HealthzReadyResponse()
    return HealthzAliveResponse()


@default_meta_blueprint.route("/url_map", methods=["GET"])
def view_url_map():
    return get_url_map()


@dataclass(kw_only=True)
class MetaBlueprintConfig:
    name: str = "meta"
    prefix: str = "/meta"
    import_name: str = __name__
    ready_callback: t.Callable[[], bool] | None = None
    alive_callback: t.Callable[[], bool] | None = None
    debug_info_callback: t.Callable[[], Flask_Response] | None = None


def _generate_meta_view(
    name: str = "meta",
    prefix: str = "/meta",
    import_name: str = __name__,
    ready_callback: t.Callable[[], bool] | None = None,
    alive_callback: t.Callable[[], bool] | None = None,
    debug_info_callback: t.Callable[[], Flask_Response] | None = None,
) -> Blueprint:
    """
    Convenience function to generate and return a 'meta' view for a Flask app.
    A 'meta' view in this sense is defined as one that handles liveness/readiness probes,
    returns debug info or provides a URL map
    """
    meta_bp = Blueprint(name, import_name=import_name, url_prefix=prefix)

    @default_meta_blueprint.route("/livez", methods=["GET"])
    def livez():
        if alive_callback is not None and not alive_callback():
            return HealthzNOTAliveResponse()
        return HealthzAliveResponse()

    @default_meta_blueprint.route("/readyz", methods=["GET"])
    def readyz():
        if ready_callback is not None and not ready_callback():
            return HealthzNOTReadyResponse()
        return HealthzReadyResponse()

    @default_meta_blueprint.route("/healthz", methods=["GET"])
    def healthz():
        if "ready" in request.args:
            return readyz()
        return livez()

    @meta_bp.route("/url_map", methods=["GET"])
    def view_url_map():
        return get_url_map()

    @meta_bp.route("/debug_info", methods=["GET"])
    def debug_info():
        if debug_info_callback is not None:
            return debug_info_callback()
        return HTTPResponse("Not found", status=404)

    return meta_bp


def generate_meta_view(config: MetaBlueprintConfig):
    return _generate_meta_view(
        name=config.name,
        prefix=config.prefix,
        import_name=config.import_name,
        ready_callback=config.ready_callback,
        alive_callback=config.alive_callback,
        debug_info_callback=config.debug_info_callback,
    )

from __future__ import annotations

from kvcommon.exceptions import DependencyException

try:
    import flask

except ImportError:
    raise DependencyException("KVCommon: Must specify 'flask' extra to use flask features.")

from __future__ import annotations

from typing import Generic
from typing import Type
from typing import TypeVar

from kvcommon.exceptions import DependencyException
from kvcommon.exceptions import KVCException

from kvcommon.misc.entities import NamedObject

try:
    import kubernetes

except ImportError:
    raise DependencyException("KVCommon: Must specify 'k8s' extra to use kubernetes features.")

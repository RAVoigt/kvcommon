import json
from typing import Generic
from typing import Type
from typing import TypeVar
from typing import Self

from kvcommon.logger import get_logger

LOG = get_logger("iapmanager")


class NamedObject:
    name: str


class NamespacedObject(NamedObject):
    namespace: str


ObjectType = TypeVar("ObjectType")


class ObjectStore(Generic[ObjectType]):
    """
    Simple type-able object store
    """

    type_var: Type[ObjectType]
    objects: dict[str, ObjectType]

    def add(self, new_obj: ObjectType, overwrite: bool = False):
        existing = self.get(new_obj.name)
        if existing and not overwrite:
            raise KeyError("Object already exists")
        self.objects[new_obj.name] = new_obj

    def get(self, ns_name: str) -> ObjectType | None:
        return self.objects.get(ns_name, None)

    def remove(self, ns_name: str) -> bool:
        removed: ObjectType | None = self.objects.pop(ns_name, None)
        if removed is not None:
            return True
        return False


class SerializableObject:
    """
    Generic serializable object that holds both its serialized JSON form and its python obj form (dict)
    """

    _serialized: str
    _deserialized: dict

    def __init__(self, serialized: str, deserialized: dict) -> None:
        self._serialized = serialized
        self._deserialized = deserialized

    def __str__(self):
        return self.serialize()

    @classmethod
    def from_json(cls, serialized: str) -> Self:
        try:
            data = json.loads(serialized)
        except json.JSONDecodeError as ex:
            LOG.error("Failed to load object from JSON: {ex}")
            raise
        return cls(serialized=serialized, deserialized=data)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        serialized = json.dumps(data, indent=4, sort_keys=True, default=str)
        return cls(serialized=serialized, deserialized=data)

    def serialize(self) -> str:
        return self._serialized

    def to_dict(self) -> dict:
        return self._deserialized.copy()

    def copy(self) -> Self:
        return self.__class__(serialized=self._serialized, deserialized=self._deserialized)

import dataclasses
import json
import typing as t

from kubernetes.client import ApiClient


def sanitize_for_serialization(model) -> dict:
    api_client = ApiClient()
    model_dict = api_client.sanitize_for_serialization(model)
    if not isinstance(model_dict, dict):
        raise TypeError(f"Unexpected type for sanitized object: '{type(model_dict).__name__}'")
    return model_dict


@dataclasses.dataclass
class FakeResponse:
    data: str


def create_fake_api_response(data: str|dict) -> FakeResponse:
    if isinstance(data, dict):
        data = json.dumps(data)
    return FakeResponse(data=data)


def to_k8s_model(model_cls: t.Type, obj_data: str|dict):
    """
    The k8s lib doesn't expose a public deserialization function that operates on a raw dict
    So we have to do this insane hoop-jumping of creating a fake response object with a .data attr

    All in service of avoiding using snake_case attr names for objects that have camelCase in k8s
    """
    api_client = ApiClient()
    fake_response = create_fake_api_response(obj_data)
    return api_client.deserialize(fake_response, response_type=model_cls)

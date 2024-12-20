from flask import jsonify
from flask import Response
from flask import Blueprint

from .meta import generate_meta_view
from .meta import MetaBlueprintConfig


class BlueprintsDict(dict):

    @staticmethod
    def _typecheck_key(key: str):
        if not isinstance(key, str):
            raise KeyError(
                "Key in BlueprintsDict must be a string representing the prefix a Flask blueprint will map to."
            )

    @staticmethod
    def _typecheck_value(blueprint: Blueprint):
        if not isinstance(blueprint, str):
            raise ValueError("Value in BlueprintsDict must be a Flask Blueprint.")

    def __setitem__(self, prefix: str, blueprint: Blueprint):
        self._typecheck_key(prefix)
        self._typecheck_value(blueprint)
        super().__setitem__(prefix, blueprint)

    def __getitem__(self, prefix: str) -> Blueprint:
        self._typecheck_key(prefix)
        value = super().__getitem__(prefix)
        self._typecheck_value(value)
        return value

    def get(self, key: str, *args, **kwargs) -> Blueprint:
        self._typecheck_key(key)
        return super().get(key, args, **kwargs)

    def pop(self, key: str, *args, **kwargs) -> Blueprint:
        self._typecheck_key(key)
        return super().pop(key, args, **kwargs)


def get_url_map() -> Response:
    from flask import current_app as app

    url_map = app.url_map
    rules_dict = dict()
    for rule in url_map.iter_rules():
        rule_dict = dict()
        rule_dict["route"] = rule.rule
        rule_dict["methods"] = str(rule.methods)
        rules_dict[rule.endpoint] = rule_dict
    return jsonify(rules_dict)

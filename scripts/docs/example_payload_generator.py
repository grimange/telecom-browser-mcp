from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExamplePayload:
    payload: dict[str, Any]
    method: str


def _placeholder_for_field(field_name: str, schema: dict[str, Any]) -> Any:
    if field_name == "target_url":
        return "https://example.invalid"
    if field_name == "session_id":
        return "<example-session-id>"
    typ = schema.get("type")
    if typ == "string":
        return "<example-string>"
    if typ in {"integer", "number"}:
        return 123
    if typ == "boolean":
        return True
    if typ == "object":
        return {}
    if typ == "array":
        return []
    return "<example-value>"


def _schema_example_value(schema: dict[str, Any]) -> tuple[bool, Any]:
    if "examples" in schema and isinstance(schema["examples"], list) and schema["examples"]:
        return True, schema["examples"][0]
    if "example" in schema:
        return True, schema["example"]
    return False, None


def _schema_default_value(schema: dict[str, Any]) -> tuple[bool, Any]:
    if "default" in schema:
        return True, schema["default"]
    return False, None


def _resolve_property_schema(schema: dict[str, Any]) -> dict[str, Any]:
    any_of = schema.get("anyOf")
    if isinstance(any_of, list):
        for option in any_of:
            if isinstance(option, dict) and option.get("type") != "null":
                return option
    return schema


def build_example_payload(input_schema: dict[str, Any]) -> ExamplePayload:
    properties = input_schema.get("properties", {})
    required = set(input_schema.get("required", []))
    payload: dict[str, Any] = {}
    methods_used: set[str] = set()

    for field_name in sorted(properties.keys()):
        raw_schema = properties[field_name]
        field_schema = _resolve_property_schema(raw_schema)

        has_example, example_value = _schema_example_value(field_schema)
        if has_example:
            payload[field_name] = example_value
            methods_used.add("schema_example")
            continue

        has_default, default_value = _schema_default_value(raw_schema)
        if has_default:
            payload[field_name] = default_value
            methods_used.add("schema_default")
            continue

        if field_name in required:
            payload[field_name] = _placeholder_for_field(field_name, field_schema)
            methods_used.add("placeholder")

    if "schema_example" in methods_used:
        method = "schema_example"
    elif "schema_default" in methods_used and "placeholder" not in methods_used:
        method = "schema_default"
    else:
        method = "placeholder"

    return ExamplePayload(payload=payload, method=method)

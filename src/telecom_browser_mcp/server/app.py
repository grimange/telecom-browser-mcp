from __future__ import annotations

import inspect
import json
from typing import Any

from telecom_browser_mcp.config.settings import Settings
from telecom_browser_mcp.tools.orchestrator import ToolOrchestrator


class TelecomBrowserApp:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.orchestrator = ToolOrchestrator(self.settings)

    @staticmethod
    def _normalize_legacy_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
        # Legacy clients may wrap all tool inputs in a single "kwargs" field.
        if set(kwargs.keys()) != {"kwargs"}:
            return kwargs
        payload = kwargs.get("kwargs")
        if payload in (None, ""):
            return {}
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, str):
            try:
                decoded = json.loads(payload)
            except json.JSONDecodeError as exc:
                raise ValueError("invalid legacy kwargs wrapper: payload is not valid JSON") from exc
            if isinstance(decoded, dict):
                return decoded
            raise ValueError("invalid legacy kwargs wrapper: decoded payload must be a JSON object")
        raise ValueError("invalid legacy kwargs wrapper: payload must be an object or JSON object string")

    @staticmethod
    def _validate_dispatch_kwargs(tool_name: str, handler: Any, kwargs: dict[str, Any]) -> None:
        signature = inspect.signature(handler)
        parameters = signature.parameters
        accepts_var_kwargs = any(param.kind is inspect.Parameter.VAR_KEYWORD for param in parameters.values())
        allowed_keys = {
            name
            for name, param in parameters.items()
            if param.kind
            in {
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            }
        }
        required_keys = {
            name
            for name, param in parameters.items()
            if param.kind
            in {
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            }
            and param.default is inspect.Parameter.empty
        }

        if not accepts_var_kwargs:
            unexpected = sorted(set(kwargs.keys()) - allowed_keys)
            if unexpected:
                names = ", ".join(unexpected)
                raise ValueError(f"invalid arguments for tool '{tool_name}': unexpected field(s): {names}")

        missing = sorted(required_keys - set(kwargs.keys()))
        if missing:
            names = ", ".join(missing)
            raise ValueError(f"invalid arguments for tool '{tool_name}': missing required field(s): {names}")

    async def dispatch(self, tool_name: str, **kwargs):
        handler = getattr(self.orchestrator, tool_name, None)
        if handler is None:
            raise ValueError(f"unknown tool: {tool_name}")
        normalized_kwargs = self._normalize_legacy_kwargs(kwargs)
        self._validate_dispatch_kwargs(tool_name, handler, normalized_kwargs)
        return await handler(**normalized_kwargs)

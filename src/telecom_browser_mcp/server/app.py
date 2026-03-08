from __future__ import annotations

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
            except json.JSONDecodeError:
                return kwargs
            if isinstance(decoded, dict):
                return decoded
        return kwargs

    async def dispatch(self, tool_name: str, **kwargs):
        handler = getattr(self.orchestrator, tool_name, None)
        if handler is None:
            raise ValueError(f"unknown tool: {tool_name}")
        normalized_kwargs = self._normalize_legacy_kwargs(kwargs)
        return await handler(**normalized_kwargs)

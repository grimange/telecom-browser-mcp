from __future__ import annotations

from telecom_browser_mcp.config.settings import Settings
from telecom_browser_mcp.tools.orchestrator import ToolOrchestrator


class TelecomBrowserApp:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.orchestrator = ToolOrchestrator(self.settings)

    async def dispatch(self, tool_name: str, **kwargs):
        handler = getattr(self.orchestrator, tool_name, None)
        if handler is None:
            raise ValueError(f"unknown tool: {tool_name}")
        return await handler(**kwargs)

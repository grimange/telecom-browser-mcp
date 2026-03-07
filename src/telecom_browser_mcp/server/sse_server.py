from __future__ import annotations

from telecom_browser_mcp.config.settings import Settings
from telecom_browser_mcp.server.app import TelecomBrowserApp
from telecom_browser_mcp.server.stdio_server import _register_tools_with_fastmcp


def main() -> None:
    settings = Settings.from_env()
    app = TelecomBrowserApp(settings)
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:
        raise SystemExit(
            "mcp SDK is unavailable; install dependencies with `pip install -e .[dev]` "
            f"(import error: {exc})"
        )

    server = FastMCP("telecom-browser-mcp")
    _register_tools_with_fastmcp(server, app)

    # SSE remains an explicit compatibility path for hosts that still prefer it.
    try:
        server.run(transport="sse", host=settings.host, port=settings.port)
    except TypeError:
        server.run(transport="sse")

import importlib

MODULES = [
    "telecom_browser_mcp",
    "telecom_browser_mcp.server.app",
    "telecom_browser_mcp.server.stdio_server",
    "telecom_browser_mcp.tools.orchestrator",
    "telecom_browser_mcp.adapters.registry",
    "telecom_browser_mcp.models.envelope",
]


def test_imports() -> None:
    for module in MODULES:
        importlib.import_module(module)

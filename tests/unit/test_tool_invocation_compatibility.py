import asyncio
import inspect

from telecom_browser_mcp.server.app import TelecomBrowserApp
from telecom_browser_mcp.server.stdio_server import _register_tools_with_fastmcp


class _FakeFastMCP:
    def __init__(self) -> None:
        self.registered: dict[str, object] = {}

    def tool(self, name: str | None = None, **_kwargs):
        def _decorator(fn):
            self.registered[name or fn.__name__] = fn
            return fn

        return _decorator


def test_registered_tools_expose_orchestrator_signatures() -> None:
    app = TelecomBrowserApp()
    fake_server = _FakeFastMCP()

    _register_tools_with_fastmcp(fake_server, app)

    list_sessions_sig = inspect.signature(fake_server.registered["list_sessions"])
    assert len(list_sessions_sig.parameters) == 0

    open_app_sig = inspect.signature(fake_server.registered["open_app"])
    assert tuple(open_app_sig.parameters.keys()) == ("url", "adapter_name")


def test_dispatch_accepts_legacy_kwargs_wrapper_payload() -> None:
    app = TelecomBrowserApp()
    result = asyncio.run(app.dispatch("list_sessions", kwargs="{}"))
    assert result["ok"] is True
    assert result["message"] == "sessions listed"

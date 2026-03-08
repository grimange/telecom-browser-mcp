import asyncio
import inspect

import pytest

from telecom_browser_mcp.server.app import TelecomBrowserApp
from telecom_browser_mcp.server.stdio_server import TOOL_NAMES, _register_tools_with_fastmcp


class _FakeFastMCP:
    def __init__(self) -> None:
        self.registered: dict[str, object] = {}

    def tool(self, name: str | None = None, **_kwargs):
        def _decorator(fn):
            self.registered[name or fn.__name__] = fn
            return fn

        return _decorator


def test_registered_tools_bind_direct_orchestrator_methods() -> None:
    app = TelecomBrowserApp()
    fake_server = _FakeFastMCP()

    _register_tools_with_fastmcp(fake_server, app)

    for tool_name in TOOL_NAMES:
        registered_handler = fake_server.registered[tool_name]
        expected_handler = getattr(app.orchestrator, tool_name)

        assert inspect.ismethod(registered_handler)
        assert registered_handler.__self__ is app.orchestrator
        assert registered_handler.__func__ is expected_handler.__func__

        signature = inspect.signature(registered_handler)
        expected_signature = inspect.signature(expected_handler)
        assert tuple(signature.parameters.keys()) == tuple(expected_signature.parameters.keys())
        assert all(
            p.kind is not inspect.Parameter.VAR_KEYWORD for p in signature.parameters.values()
        ), f"synthetic **kwargs wrapper detected for tool: {tool_name}"


def test_dispatch_accepts_legacy_kwargs_wrapper_payload() -> None:
    app = TelecomBrowserApp()
    result = asyncio.run(app.dispatch("list_sessions", kwargs="{}"))
    assert result["ok"] is True
    assert result["message"] == "sessions listed"


def test_dispatch_accepts_legacy_kwargs_optional_arg_payload() -> None:
    app = TelecomBrowserApp()
    result = asyncio.run(app.dispatch("capabilities", kwargs='{"include_groups": false}'))
    assert result["ok"] is True
    assert result["data"]["include_groups"] is False
    assert "tool_groups" not in result["data"]


def test_dispatch_rejects_malformed_legacy_kwargs_wrapper_payload() -> None:
    app = TelecomBrowserApp()
    with pytest.raises(ValueError, match="invalid legacy kwargs wrapper"):
        asyncio.run(app.dispatch("list_sessions", kwargs="{"))


def test_dispatch_rejects_unknown_fields_before_handler_call() -> None:
    app = TelecomBrowserApp()
    with pytest.raises(ValueError, match="unexpected field\\(s\\): unexpected"):
        asyncio.run(app.dispatch("list_sessions", kwargs='{"unexpected": true}'))


def test_dispatch_does_not_forward_nested_kwargs_key() -> None:
    app = TelecomBrowserApp()
    with pytest.raises(ValueError, match="unexpected field\\(s\\): kwargs"):
        asyncio.run(app.dispatch("list_sessions", kwargs={"kwargs": {}}))


def test_dispatch_rejects_missing_required_fields() -> None:
    app = TelecomBrowserApp()
    with pytest.raises(ValueError, match="missing required field\\(s\\): url"):
        asyncio.run(app.dispatch("open_app"))

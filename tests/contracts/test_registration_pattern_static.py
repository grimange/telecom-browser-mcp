from __future__ import annotations

import ast
from pathlib import Path


SRC_ROOT = Path("src/telecom_browser_mcp")
SERVER_DIR = SRC_ROOT / "server"
STDIO_SERVER = SERVER_DIR / "stdio_server.py"


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _find_register_fn(module: ast.Module) -> ast.FunctionDef:
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_register_tools_with_fastmcp":
            return node
    raise AssertionError("missing _register_tools_with_fastmcp")


def test_canonical_registration_site_is_unique() -> None:
    hits: list[Path] = []
    for path in SERVER_DIR.glob("*.py"):
        if "server.tool(" in path.read_text(encoding="utf-8"):
            hits.append(path)

    assert hits == [STDIO_SERVER], f"expected only stdio_server registration site, got: {hits}"


def test_register_function_binds_direct_handler() -> None:
    module = _parse(STDIO_SERVER)
    register_fn = _find_register_fn(module)

    direct_bind_call_found = False
    for node in ast.walk(register_fn):
        if not isinstance(node, ast.Call):
            continue
        # Match: server.tool(name=tool_name)(handler)
        if (
            isinstance(node.func, ast.Call)
            and isinstance(node.func.func, ast.Attribute)
            and isinstance(node.func.func.value, ast.Name)
            and node.func.func.value.id == "server"
            and node.func.func.attr == "tool"
            and len(node.func.args) == 0
            and len(node.func.keywords) == 1
            and node.func.keywords[0].arg == "name"
            and isinstance(node.func.keywords[0].value, ast.Name)
            and node.func.keywords[0].value.id == "tool_name"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id == "handler"
        ):
            direct_bind_call_found = True
            break

    assert direct_bind_call_found, "expected direct server.tool(name=tool_name)(handler) binding"


def test_register_function_has_no_nested_kwargs_wrapper() -> None:
    module = _parse(STDIO_SERVER)
    register_fn = _find_register_fn(module)

    nested_functions = [
        node
        for node in ast.walk(register_fn)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node is not register_fn
    ]

    for nested in nested_functions:
        assert nested.args.kwarg is None, (
            f"synthetic **kwargs wrapper detected in registration path: {nested.name}"
        )

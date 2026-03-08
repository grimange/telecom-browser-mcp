# 02 - Canonical Validation Profile

## Discovery Set
- bootstrap and registration path
- first-contact tool visibility and invocability (`health`, `capabilities`, `list_sessions`)
- canonical tool-set consistency guard

## Invocation Set
- no-arg tool: `health({})`
- arg-bearing tool: `open_app({...})`
- optional/nullable path: optional args in `open_app` and `collect_debug_bundle`
- malformed input path: undeclared field => `invalid_input`
- unknown/extra argument handling: validated across tool model map

## Runtime Set
- stateful multi-call workflow (service-level)
- predictable failure (`session_not_found`)
- transport runtime first-contact across stdio/SSE/streamable-http

## Commands Used
- `. .venv/bin/activate && pytest -q tests/contract/test_m1_tool_envelopes.py tests/contract/test_schema_runtime_parity.py`
- `. .venv/bin/activate && pytest -q tests/integration/test_server_registration.py tests/integration/test_transport_entrypoints.py`
- `. .venv/bin/activate && MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1 pytest -q tests/integration/test_stdio_smoke.py tests/integration/test_http_transport_smoke.py`

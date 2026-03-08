# 02 - Canonical Validation Profile

## Discovery Set
- Server registration/loading: `create_mcp_server()` bootstrap and entrypoint wiring
- Tool listing visibility: `health`, `capabilities`, `list_sessions` presence checks in stdio smoke harness
- Schema visibility/accessibility: generated schemas in `docs/contracts/m1/`
- Metadata consistency: tool set equality assertion between registration and canonical map

## Invocation Set
- Minimal/no-argument tool: `health({})`
- Argument-bearing tool: `open_app({"target_url": "https://example.com"})`
- Optional/nullable parameter case: `open_app(adapter_id=None, session_label=None)`/`collect_debug_bundle(reason=None)` contract path
- Malformed input case: undeclared field rejected with `error.code = "invalid_input"`
- Unknown/extra argument case: same undeclared-field parity test across all tools

## Runtime Set
- Stateful multi-call workflow: open session -> login/wait/answer/snapshot/close (service-level envelope test)
- Predictable failure path: missing-session calls return `session_not_found`
- Diagnostic usefulness check: canonical envelope always includes `diagnostics` and `artifacts`

## Canonical Commands Executed
- `. .venv/bin/activate && pytest -q tests/contract/test_m1_tool_envelopes.py tests/contract/test_schema_runtime_parity.py`
- `. .venv/bin/activate && pytest -q tests/integration/test_server_registration.py tests/integration/test_transport_entrypoints.py`
- `. .venv/bin/activate && pytest -q -rs tests/integration/test_stdio_smoke.py tests/integration/test_http_transport_smoke.py`

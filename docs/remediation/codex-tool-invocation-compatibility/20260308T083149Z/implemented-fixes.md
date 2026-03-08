# Implemented Fixes

## Code changes

1. Signature-aligned tool registration
- File: `src/telecom_browser_mcp/server/stdio_server.py`
- Change: wrappers now set `__signature__` from orchestrator methods before registration.
- Result: MCP tool schemas reflect real parameters instead of synthetic wrapper payloads.

2. Legacy kwargs compatibility shim
- File: `src/telecom_browser_mcp/server/app.py`
- Change: `_normalize_legacy_kwargs` unwraps `{ "kwargs": <dict-or-json> }` into canonical kwargs.
- Result: older clients that still send wrapped payloads no longer fail on binding.

3. Safe first-contact tools
- File: `src/telecom_browser_mcp/tools/orchestrator.py`
- Change: added `health()` and `capabilities(include_groups: bool = True)`.
- Result: deterministic no-arg tool path for post-registration smoke checks.

4. Tool catalog updated
- File: `src/telecom_browser_mcp/server/stdio_server.py`
- Change: added `health`, `capabilities` to `TOOL_NAMES`.

5. Contract tests updated
- File: `tests/unit/test_tool_discovery_contract.py`
- Change: expected tool set includes new safe tools.

6. New invocation compatibility tests
- File: `tests/unit/test_tool_invocation_compatibility.py`
- Change: validates exported wrapper signatures and legacy `kwargs` dispatch compatibility.

7. Documentation updates
- Files: `README.md`, `docs/usage/codex-agent-usage.md`, `AGENTS.md`
- Change: added safe first-call guidance (`health`, `capabilities`, `list_sessions`).

## Verification executed

- `.venv/bin/pytest -q tests/unit`
  - result: `8 passed`

- `PYTHONPATH=src .venv/bin/pytest -q`
  - result: `95 passed`

- In-process dispatcher smoke:
  - artifact: `smoke-test-results.json`
  - result: no `unexpected keyword argument 'kwargs'` observed.

## Environment limitation observed

Wire-level stdio probe in this sandbox failed with subprocess bootstrap import mismatch (`ModuleNotFoundError: anyio`). This is recorded as an environment limitation and did not block dispatcher-level compatibility verification.

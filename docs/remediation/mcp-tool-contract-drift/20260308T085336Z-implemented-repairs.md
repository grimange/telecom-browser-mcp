# Implemented Repairs

- timestamp: 2026-03-08T08:53:36Z

## Code Changes

1. `src/telecom_browser_mcp/server/stdio_server.py`
- removed synthetic `**kwargs` wrapper registration path.
- registered MCP tools directly against orchestrator handlers.
- enforced strict argument validation by setting FastMCP argument model `extra=forbid`.

2. `tests/unit/test_tool_invocation_compatibility.py`
- updated fake FastMCP decorator shim to support named registration (`tool(name=...)`).

3. `tests/contracts/test_tool_contract_parity.py` (new)
- added T1-T6 contract validation suite:
  - tool listing integrity
  - valid no-arg invocation
  - invalid envelope rejection
  - no-arg schema shape
  - strict schema enforcement
  - signature/schema parity

4. `.github/workflows/tool-contracts.yml` (new)
- added CI jobs:
  - `tool_contract_schema_parity`
  - `tool_contract_invocation_smoke`
  - `tool_contract_strictness_checks`

## Validation Run

Command:

`PYTHONPATH=src .venv/bin/pytest -q tests/contracts/test_tool_contract_parity.py tests/unit/test_tool_invocation_compatibility.py tests/e2e/test_stdio_smoke.py`

Result:

`9 passed in 0.55s`

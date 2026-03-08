# Static Contract Guardrails

- Timestamp: `20260308T094744Z`

## Canonical Registration Pattern

Approved pattern:

- registration function: `_register_tools_with_fastmcp(server, app)`
- binding shape: `server.tool(name=tool_name)(handler)`
- handler source: bound `ToolOrchestrator` methods
- strict argument model: `ArgModelBase.model_config.extra = "forbid"`

Disallowed public patterns:

- synthetic wrapper registrations using `**kwargs`
- wrapper call signatures that differ from runtime handler signatures
- public schemas exposing synthetic `kwargs` fields

## Exposed Tool States

1. No-input tools:
- `health`
- `list_sessions`

2. Explicit-parameter tools:
- all remaining tools in `TOOL_NAMES` (session_id/url/timeout/etc.)

3. Validated request-object internal path with explicit public contract:
- internal helper only: `TelecomBrowserApp.dispatch(...)`
- legacy `{ "kwargs": ... }` envelope is deprecated compatibility behavior, not public MCP contract.

## Enforcement

- static tests: `tests/contracts/test_tool_contract_parity.py`
- pattern tests: `tests/contracts/test_registration_pattern_static.py`
- dispatch compatibility tests: `tests/unit/test_tool_invocation_compatibility.py`
- CI guardrail script: `scripts/check_static_contract_guardrails.sh`

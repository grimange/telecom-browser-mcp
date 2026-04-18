# Langchain Integration

## Status
- unverified integration pattern

## Verification Summary
- Startup contract: high confidence (static code + entrypoint evidence).
- Tool discovery: high confidence (registry export).
- Invocation success: unverified for this agent integration surface in this run.
- Workflow validity: medium confidence from host-required tests and verification docs.

## Startup Contract
- Canonical command: `telecom-browser-mcp`
- Stdio command: `telecom-browser-mcp-stdio`
- Streamable HTTP command: `telecom-browser-mcp-http`
- SSE command: `telecom-browser-mcp-sse`

## Transport
- Integration surface for this guide: `streamable-http`
- Supported transports: stdio, streamable-http, sse
- Default transport: `stdio`

## Configuration Example
```python
# Local launch example:
# FASTMCP_HOST=127.0.0.1 FASTMCP_PORT=8000 telecom-browser-mcp-http
MCP_ENDPOINT = "http://127.0.0.1:8000/mcp"
```

Syntax provenance:
- pyproject.toml:[project.scripts].telecom-browser-mcp-http
- src/telecom_browser_mcp/server/streamable_http_server.py

## Tool Discovery Expectations
- Expected tool count: `17`
- First-contact checks should succeed: `health`, `capabilities`, `list_sessions`.
- Session-bound tools require `session_id` returned by `open_app`.

## Minimal Safe Workflow
- `first-contact-safe-discovery` (validated_policy, confidence=high):
  health -> capabilities -> list_sessions
  Evidence: AGENTS.md::Codex First-Contact Tool Guidance
- `inbound-answer-happy-path` (host_required_e2e, confidence=medium):
  open_app -> wait_for_ready -> wait_for_registration -> wait_for_incoming_call -> answer_call -> get_registration_status -> get_store_snapshot -> hangup_call -> close_session
  Evidence: tests/e2e/test_fake_dialer_harness.py::test_inbound_answer_success, docs/verification/agent-readiness/telecom-browser-mcp/20260308T140345Z/03-workflow-validation.md
- `answer-failure-diagnostics` (host_required_e2e, confidence=medium):
  open_app -> wait_for_ready -> wait_for_registration -> wait_for_incoming_call -> answer_call -> diagnose_answer_failure -> collect_debug_bundle -> close_session
  Evidence: tests/e2e/test_fake_dialer_harness.py::test_inbound_answer_failure_generates_diagnostics_and_bundle

## Environment Variables and Prerequisites
Prerequisites:
- Python 3.11+
- project dependencies from pyproject.toml
- Playwright browser binaries installed in host runtime for browser-driving tools

Environment variables:
- `FASTMCP_HOST` (optional)
- `FASTMCP_PORT` (optional)
- `TELECOM_BROWSER_MCP_DOCGEN` (optional)

## Troubleshooting
- `environment_limit_missing_browser_binary`: Browser-driving tools can degrade when Playwright browser binaries are unavailable.
- `environment_limit_unreachable_target`: open_app can fail/degrade when target URL is unreachable.
- `permission_blocked`: Sandbox/runtime restrictions can block browser launch or transport sockets.
- If browser-driving flows fail in sandboxed runtime, classify as environment limitation unless host runtime reproduces the defect.

## Open Verification Gaps
- No agent-specific live `tools/list` transcript is captured in this generation run.
- No agent-specific `tools/call` transcript is captured in this generation run.
- Runtime behavior claims are downgraded to unverified integration pattern until host validation evidence is attached.

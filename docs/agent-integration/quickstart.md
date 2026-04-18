# Agent Integration Quickstart

Generated at: `20260308T152757Z`

## Server Startup Command
```bash
TELECOM_BROWSER_MCP_DOCGEN=1 telecom-browser-mcp-stdio
```

## Transport Type
Default transport: `stdio`
Supported transports: stdio, streamable-http, sse

## Tool Discovery Expectations
- Expected tool count: `17`
- First-contact checks should succeed: `health`, `capabilities`, `list_sessions`.
- Session-bound tools require `session_id` returned by `open_app`.
- Session-bound responses stamp adapter identity in `meta`:
  `contract_version`, `adapter_id`, `adapter_name`, `adapter_version`, `scenario_id`.

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

## Verification Boundaries
- Guides include startup, schemas, and configuration patterns from static and contract evidence.
- Runtime compatibility claims are intentionally downgraded unless live evidence is present.
- APNTalk compatibility remains fail-closed until verified selectors and runtime probes land; do not treat APNTalk ready/registration/call actions as implemented based only on scaffold presence.

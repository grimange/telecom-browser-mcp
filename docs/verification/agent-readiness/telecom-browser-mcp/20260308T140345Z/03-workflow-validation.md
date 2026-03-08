# 03 - Workflow Validation

## Workflow Under Verification
`health -> capabilities -> list_sessions -> open_app -> login_agent -> wait_for_registration -> wait_for_incoming_call -> answer_call -> collect_debug_bundle`

## Preconditions and Transitions
- First-contact tools are registered and callable (`src/telecom_browser_mcp/server/app.py:19`, `tests/integration/test_stdio_smoke.py:29`).
- `open_app` exposes `ready_for_actions` gating signal (`src/telecom_browser_mcp/tools/service.py:244`, `README.md:48`).
- Session-bound tools require valid session and enforce lifecycle checks (`src/telecom_browser_mcp/tools/service.py:86`, `src/telecom_browser_mcp/tools/service.py:348`).
- Failure branch of `answer_call` captures diagnostics + evidence bundle (`src/telecom_browser_mcp/tools/service.py:473`).

## Composability Assessment
- Tool chaining is explicit and state-based; no hidden `kwargs` wrapper dependency.
- Contract tests and harness e2e tests cover multi-step call patterns (`tests/contract/test_m1_tool_envelopes.py:23`, `tests/e2e/test_fake_dialer_harness.py:41`).

## Verification Limits
- End-to-end runtime validation for networked transports is environment-gated (skips).
- Browser/telecom live workflow remains host-dependent.

Evidence tier: `static_verified` + `test_verified` + `unable_to_verify` (for full transport runtime).

## Workflow Verdict
- Contractual workflow composition is valid.
- Runtime interoperability evidence across all client transports is incomplete in this environment.

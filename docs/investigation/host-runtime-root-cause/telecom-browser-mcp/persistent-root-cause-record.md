# Persistent Root Cause Record

Date: 2026-03-08
Project: `telecom-browser-mcp`

Persistent conclusion:

- MCP host blocker classification: `environment_specific_stdio_behavior`
- Browser host blocker classification: `chromium_sandbox_policy_block`

Evidence-backed statement:

- The MCP server does not appear to be blocked by its own startup path. Instead, on this host, async stdio reading strategies used by the SDK and by the current workaround both fail to deliver initialize input to the running server process.
- The browser blocker is independent of MCP and reproduces in direct standalone Chromium execution with explicit sandbox-disabling flags, which makes it a host policy/runtime issue rather than an adapter or orchestration defect.

Next remediation pipeline:

1. Replace host verification of MCP stdio with either:
   - a truly synchronous stdio bridge for this server, or
   - an alternate verification transport on this host if stdio remains unreliable.
2. Move browser validation to a host/runtime that permits Chromium launch, or use a remote browser target instead of local Chromium on this host.
3. Re-run `016 Controlled Live Verification` only after both host blockers are addressed with targeted remediation.

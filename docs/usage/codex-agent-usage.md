# Codex Agent Usage

## When to use this MCP

Use `telecom-browser-mcp` when an agent needs telecom-intent browser
operations, such as:

- `open_app`
- `wait_for_registration`
- `wait_for_incoming_call`
- `answer_call`
- `get_peer_connection_summary`
- `diagnose_answer_failure`

## Host vs sandbox rule

- Browser-driving telecom operations should run in a host/runtime that
  can launch Chromium.
- Sandbox failures (stdio timeout, browser launch restriction, blocked
  websocket/media prerequisites) are environment findings unless host
  evidence reproduces the defect.

## Recommended execution sequence

1. Register MCP server with Codex.
2. Call `health` and `capabilities` with no arguments.
3. Call `list_sessions` with no arguments.
4. Run `scripts/run_mcp_interop_probe.py` to verify handshake/tool discovery.
5. Run telecom tools against harness or target app.
6. Collect `collect_debug_bundle` and diagnostics before remediation.

## Avoid

- Treating sandbox-only failures as product regressions
- Using generic selector-click tooling instead of telecom-intent tools
- Claiming live telecom validation without host evidence

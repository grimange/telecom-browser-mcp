# Host vs Sandbox Policy

## Principle

`environment truth before code remediation`

## Policy statements

- Browser-driving telecom workflows are host-first operations.
- Sandbox stdio/browser failures are environment signals unless reproduced in approved host runtime.
- Release/integration decisions must prioritize host-pass probe artifacts over sandbox-only no-response outcomes.

## Classification matrix

- Host `ok=true` and sandbox `ok=false` (stdio no-response): classify as `environment variance`, not product defect.
- Host `ok=false` with reproducible initialize/list-tools failure: classify as `integration blocker`.
- Host pass for handshake but browser launch blocked by host policy: classify as `host runtime constraint`, not MCP contract defect.

## Required evidence for remediation decisions

1. Host interop probe artifact (`scripts/run_mcp_interop_probe.py`).
2. Sandbox probe artifact (if available) to show variance.
3. Tool contract test evidence (`tests/unit/test_tool_discovery_contract.py`).

## Operational guidance for agents

- Stop short of code remediation when only sandbox limits are observed.
- Produce host-run instructions and evidence requests.
- Proceed to remediation only when host-approved evidence indicates product behavior drift.

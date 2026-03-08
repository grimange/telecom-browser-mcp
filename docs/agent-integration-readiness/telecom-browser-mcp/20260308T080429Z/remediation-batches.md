# Remediation Batches

## Batch 1 - Integration blockers

Priority: high

- Add a stable host verification runbook entry that explicitly gates remediation on host interop evidence.
- Keep `scripts/run_mcp_interop_probe.py` as canonical handshake check in operator docs.

Exit criteria:

- Host run instructions + expected artifact paths are documented in one setup surface.

## Batch 2 - Guidance blockers

Priority: high

- Completed in this run:
  - `AGENTS.md` host execution policy added.
  - `README.md` Codex registration + host/sandbox guidance added.
  - `docs/usage/codex-agent-usage.md` added.

Exit criteria:

- Agents receive explicit host-first instruction for browser-driving tools.

## Batch 3 - Interoperability blockers

Priority: medium

- Continue collecting both host and sandbox probe results for divergence tracking.
- If host intermittency appears, add deterministic stdio trace instrumentation for startup/initialize timing.

Exit criteria:

- Host interop probe remains stable across repeated runs.

## Batch 4 - Contract clarity issues

Priority: medium

- Add explicit adapter failure handling in `login_agent` and `hangup_call` to ensure consistent failure envelopes.
- Document envelope as canonical top-level error fields or introduce versioned nested error model if required.

Exit criteria:

- All action tools branch to success/failure envelope consistently.

## Batch 5 - Operator experience improvements

Priority: medium

- Maintain a single "Codex MCP setup" page and link it from README and host setup guide.
- Add quick troubleshooting table for common environment limitations.

Exit criteria:

- New operator can register and validate MCP without external context.

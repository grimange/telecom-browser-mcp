# Probe And Browser Audit

- timestamp: 2026-03-08T05:50:43Z
- pipeline: `022--resolve-host-mcp-browser-blockers`

Findings:
- Startup readiness is now handshake-derived (`startup_ready_via_handshake` required), not timeout-survival based.
- MCP probe now sends explicit JSON-RPC sequence:
  1. `initialize`
  2. `notifications/initialized`
  3. `tools/list`
- Current host still times out waiting for initialize response (`handshake_timeout`).
- Browser launch now applies host args (`--no-sandbox,--disable-setuid-sandbox,--disable-dev-shm-usage`) and `chromium_sandbox=False`.
- Current host still fails Chromium launch with sandbox host fatal (`Operation not permitted`).

Evidence:
- `docs/remediation/host-runtime/evidence/20260308T055043Z--mcp-interop-probe.json`
- `docs/remediation/host-runtime/evidence/20260308T055043Z--live-tool-checks.json`

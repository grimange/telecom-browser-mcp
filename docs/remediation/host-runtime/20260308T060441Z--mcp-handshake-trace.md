# MCP Handshake Trace

Automated raw probe behavior:
- sent initialize request with `protocolVersion=2024-11-05`
- waited for initialize response
- no response received before timeout
- classification: `handshake_timeout`
- startup_state: `startup_timeout_without_handshake`

Evidence:
- `docs/remediation/host-runtime/evidence/20260308T060441Z--automated-mcp-probe.json`
- `docs/remediation/host-runtime/evidence/mcp-interop-probe-stderr.log` (empty)

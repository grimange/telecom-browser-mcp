# Handshake Probe Fix

Implemented raw stdio handshake probe:
- module: `src/telecom_browser_mcp/mcp_handshake_probe.py`
- script: `scripts/run_mcp_handshake_probe.py`

Behavior:
- Spawns MCP server over stdio.
- Sends explicit `initialize` request (`protocolVersion=2024-11-05`).
- Sends `notifications/initialized`.
- Sends `tools/list` request.
- Captures request/response transcript in evidence payload.

Classifications:
- `handshake_passed`
- `handshake_timeout`
- `handshake_invalid_response`
- `handshake_transport_failure`

Current run:
- `classification=handshake_timeout`
- `failure=handshake_read_timeout`

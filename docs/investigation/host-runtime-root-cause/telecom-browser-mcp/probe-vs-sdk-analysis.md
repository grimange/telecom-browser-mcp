# Probe vs SDK Analysis

Raw probe result:

- Request format: newline-delimited JSON, not `Content-Length` framing.
- Initialize request payload is structurally valid for MCP:
  - `method=initialize`
  - `protocolVersion=2024-11-05`
  - JSON-RPC id present
- Result: no response, `handshake_timeout`.

Official SDK probe result:

- Uses the MCP Python SDK `ClientSession.initialize()`.
- Result: no response, `environment_blocked_stdio_no_response`.

Comparison:

- Both probes target the current workspace source through `PYTHONPATH=src`.
- Both probes wait on initialize and receive no response bytes.
- Both corresponding stderr logs are empty.

Rejected hypotheses:

- `probe_format_issue`
  - Rejected because the SDK client fails too.
- `probe_read_logic_issue`
  - Rejected because the SDK client also blocks waiting for initialize.
- `initialize payload incorrect`
  - Rejected because the payload shape matches MCP expectations and the failure is indistinguishable from the SDK client path.

Accepted interpretation:

- The probe is not the primary cause.
- The failure occurs at the host stdio behavior boundary used by both SDK and custom async reader implementations.

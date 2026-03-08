# 05 - Invocation Contract Compatibility

## Findings
- No-arg and arg-bearing invocation paths are stable in tests.
- Unknown/extra args deterministically fail with `invalid_input`.
- Missing-session paths deterministically fail with `session_not_found`.
- Strict transport first-contact invocations pass on stdio/SSE/streamable-http.

## Results by Client
| Client | Result | Evidence Type | Notes |
|---|---|---|---|
| Codex CLI | partial | static_only | no direct Codex MCP invocation transcript |
| Claude Desktop | unable_to_verify | not_available | client inaccessible |
| OpenAI Agents SDK path | partial | observed_directly | transport invocation proven; full app path not observed |
| Reference harness | pass | observed_directly | strict runtime transport invocation passed |

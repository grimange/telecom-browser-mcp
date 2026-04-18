# 03 - Discovery Compatibility

## Findings
- Server bootstrap check passes.
- Transport entrypoint routing checks pass.
- Strict transport runtime smoke now proves first-contact discovery path in harnessed clients.

## Per-Client Discovery Result
| Client | Result | Evidence Type | Notes |
|---|---|---|---|
| Codex CLI | partial | static_only + observed_indirectly | no direct Codex MCP config-run transcript |
| Claude Desktop | unable_to_verify | not_available | client inaccessible |
| OpenAI Agents SDK path | partial | observed_directly | transport-level discovery works; no full Agents app run |
| Reference harness | pass | observed_directly | live discovery/invocation proven in strict run |

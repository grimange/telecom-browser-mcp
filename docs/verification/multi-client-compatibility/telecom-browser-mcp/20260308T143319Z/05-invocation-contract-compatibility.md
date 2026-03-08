# 05 - Invocation Contract Compatibility

## Invocation Surface Validated
- No-arg invocation path: `health`, `capabilities`, `list_sessions`
- Arg-bearing path: `open_app`, `login_agent`, `wait_*`, `answer_call`, diagnostics tools
- Unknown/extra argument handling: undeclared fields return `invalid_input` for all tools
- Deterministic error behavior: missing `session_id` paths return `session_not_found`

## Results by Client
| Client | Result | Evidence Type | Rationale |
|---|---|---|---|
| Codex CLI | partial | static_only | Contract is strict in source/tests; no direct Codex tool-call transcript |
| Claude Desktop | unable_to_verify | not_available | No executable Claude environment in this run |
| OpenAI Agents SDK path | partial | test_demonstrated | Invocation logic validated by tests; live transport calls skipped |
| Reference harness | partial | observed_directly + test_demonstrated | Service-level invocation behavior passed; transport-bound client calls skipped |

## Notes
Invocation compatibility is strong at contract layer, but client/runtime interaction remains unproven for live transport in this environment.

# 06 - Error Semantics Compatibility

## Validated Error Semantics
- Invalid input (undeclared fields): `error.code = invalid_input`
- Missing session context: `error.code = session_not_found`
- Error envelopes include canonical fields: `tool`, `ok`, `error`, `diagnostics`, `artifacts`, `meta`

## Compatibility Assessment
- Contract-level semantics are deterministic and stable across tested tool handlers.
- Client-side parsing compatibility for these errors is not directly observed for Codex/Claude/OpenAI runtime clients in this run.

## Tier Result
- Contract semantics: `pass`
- Cross-client runtime semantics: `unable_to_verify`
- Evidence class: `observed_directly` (service tests), `not_available` (external client runtime)

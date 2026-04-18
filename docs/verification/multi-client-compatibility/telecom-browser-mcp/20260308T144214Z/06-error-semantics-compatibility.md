# 06 - Error Semantics Compatibility

## Validated Semantics
- `invalid_input` on undeclared fields.
- `session_not_found` on missing session operations.
- Canonical error envelope fields preserved.

## Result
- Contract-level error semantics: `pass`
- Cross-client runtime semantics:
  - Reference harness: `pass`
  - Codex CLI / Claude Desktop: `unable_to_verify`
  - OpenAI Agents SDK path: `partial`

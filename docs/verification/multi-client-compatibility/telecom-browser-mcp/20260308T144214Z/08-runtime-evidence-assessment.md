# 08 - Runtime Evidence Assessment

## Evidence Inventory
| Surface | Evidence | Class |
|---|---|---|
| service-level stateful workflow | contract envelope test | observed_directly |
| stdio runtime first-contact | strict smoke pass | observed_directly |
| SSE runtime first-contact | strict smoke pass | observed_directly |
| streamable-http runtime first-contact | strict smoke pass | observed_directly |
| Codex configured-client runtime | not executed directly | not_available |
| Claude Desktop runtime | not executed directly | not_available |

## Runtime Decision
- Reference harness runtime: `pass`
- OpenAI transport integration runtime: `partial`
- Codex CLI runtime: `unable_to_verify`
- Claude Desktop runtime: `unable_to_verify`

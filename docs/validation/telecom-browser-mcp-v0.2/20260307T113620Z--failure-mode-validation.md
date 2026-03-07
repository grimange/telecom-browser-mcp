# Failure Mode Validation (20260307T113620Z)

## Tested
- invalid arguments: PARTIAL (TypeError at call boundary, not MCP wire validation)
- missing browser state/session expiration: PASS (structured SESSION_NOT_FOUND envelope)
- missing DOM element: PARTIAL (adapter scaffold returns explicit unavailable reason)
- transport interruption: INCONCLUSIVE
- telecom event absence: PARTIAL
- timeout boundaries: PARTIAL

## Structured failure check
- Missing-session failure envelope includes required failure fields: PASS

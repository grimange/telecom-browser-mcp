# 12 - Readiness Claims Ledger

| Claim ID | Claim | Status | Confidence | Evidence Class | Evidence |
|---|---|---|---|---|---|
| C-301 | Registered tools align with canonical contracts | Confirmed | High | Source/Test | `server/app.py:75`, `m1_contracts.py:35` |
| C-302 | Published schemas match generated contracts | Confirmed | High | Schema/Test | `test_schema_runtime_parity.py:19` |
| C-303 | Runtime rejects undeclared fields | Confirmed | High | Test | `test_schema_runtime_parity.py:28` |
| C-304 | Open-app readiness semantics are explicit and machine-usable | Confirmed | High | Source/Test | `service.py:244`, `test_service_contracts.py:14` |
| C-305 | Lock contention semantics are explicit and retryable | Confirmed | High | Source/Test | `service.py:159`, `test_agent_integration_remediation.py:52` |
| C-306 | Stdio first-contact interoperability is validated | Confirmed | High | Test | `test_stdio_smoke.py:28` |
| C-307 | SSE/HTTP live interoperability is fully proven in this environment | Unverified | Low | Test/Inference | smoke tests present but may skip (`test_http_transport_smoke.py:92`) |
| C-308 | Overall integration readiness gate is met | Confirmed | Medium | Score/Method | `10-readiness-scorecard.md` |

## Notes
- C-307 is the only explicitly unverified runtime claim for this environment.

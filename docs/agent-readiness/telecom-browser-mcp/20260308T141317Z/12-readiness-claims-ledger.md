# 12 - Readiness Claims Ledger

| Claim ID | Claim | Status | Confidence | Evidence Class | Evidence |
|---|---|---|---|---|---|
| C-401 | Registered tools align with canonical contracts | Confirmed | High | Source/Test | `server/app.py:75`, `m1_contracts.py:35` |
| C-402 | Published schemas match generated contracts | Confirmed | High | Schema/Test | `test_schema_runtime_parity.py:19` |
| C-403 | Runtime rejects undeclared fields | Confirmed | High | Test | `test_schema_runtime_parity.py:29` |
| C-404 | Open-app readiness semantics are explicit | Confirmed | High | Source/Test | `service.py:244`, `test_service_contracts.py:14` |
| C-405 | Lock contention semantics are deterministic and retryable | Confirmed | High | Source/Test | `service.py:159`, `test_agent_integration_remediation.py:52` |
| C-406 | Envelope shape is stable across tool surface | Confirmed | High | Test | `test_m1_tool_envelopes.py:8` |
| C-407 | Runtime stdio/SSE/HTTP interoperability is fully proven in this environment | Unverified | Low | Test/Runtime | transport tests skipped for env limits (`test_stdio_smoke.py:66`, `test_http_transport_smoke.py:100`) |
| C-408 | Current repo is Integration Ready for agent integration | Confirmed | Medium | Score/Method | `10-readiness-scorecard.md` |

## Notes
- C-407 requires host-lane strict-mode evidence to upgrade confidence.

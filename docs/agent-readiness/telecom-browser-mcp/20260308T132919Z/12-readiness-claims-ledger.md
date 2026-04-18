# 12 - Readiness Claims Ledger

| Claim ID | Claim | Status | Evidence Class | Confidence | Evidence |
|---|---|---|---|---|---|
| C-201 | Tool registration aligns with canonical contracts | Confirmed | Source/Test | High | `server/app.py:75`, `contracts/m1_contracts.py:35` |
| C-202 | Published schema artifacts match generated contracts | Confirmed | Schema/Test | High | `test_schema_runtime_parity.py:19` |
| C-203 | Runtime rejects undeclared tool fields | Confirmed | Test | High | `test_schema_runtime_parity.py:28` |
| C-204 | Envelope structure remains stable across tools | Confirmed | Test/Source | High | `test_m1_tool_envelopes.py:8`, `models/common.py:46` |
| C-205 | `open_app` readiness semantics are machine-usable | Confirmed | Source/Test | High | `service.py:214`, `test_service_contracts.py:14` |
| C-206 | Session operations are serialized per session | Confirmed | Source/Test | High | `manager.py:20`, `service.py:250`, `test_agent_integration_remediation.py:10` |
| C-207 | Non-answer failure diagnostics are improved | Confirmed | Source/Test | Medium | `service.py:115`, `test_agent_integration_remediation.py:30` |
| C-208 | stdio first-contact interoperability is verified | Confirmed | Test | High | `test_stdio_smoke.py:28` |
| C-209 | SSE/HTTP live interoperability is fully verified | Unverified | Inference/Source | Low | transport wiring tests only (`test_transport_entrypoints.py:14`) |
| C-210 | Overall readiness gate meets Integration Ready criteria | Confirmed | Score/Method | Medium | `10-readiness-scorecard.md` |

## Notes
- Unverified claim C-209 is explicitly excluded from Release Candidate assertion.
